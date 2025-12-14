"""
API_Final_Agent - Unified Analysis Service
Single FastAPI service that merges ACE_Framework and EssenceAI pipelines.
"""

import os
import uuid
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator
import uvicorn

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from api_final_agent.pipelines.ace_pipeline import run_ace_analysis
from api_final_agent.pipelines.essence_pipeline import run_essence_analysis
from api_final_agent.unified_output import create_unified_output
from api_final_agent.investigation import investigate_outputs

app = FastAPI(
    title="API_Final_Agent - Unified Analysis Service",
    version="1.0.0",
    description="Unified service combining ACE_Framework and EssenceAI pipelines"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UnifiedRequest(BaseModel):
    """Unified input model for analysis."""
    analysis_id: Optional[str] = Field(None, description="Analysis ID (optional, generated if not provided)")
    business_objective: str = Field(..., description="Business objective (required)")
    barcode: Optional[str] = Field(None, description="Product barcode for ACE pipeline")
    product_link: Optional[str] = Field(None, description="Product URL for Essence pipeline")
    product_description: Optional[str] = Field(None, description="Product description for Essence pipeline")
    domain: Optional[str] = Field(None, description="Domain filter for Essence (e.g., 'Plant-Based')")
    segment: Optional[str] = Field(None, description="Segment filter for Essence (e.g., 'Skeptic')")
    
    @model_validator(mode='after')
    def validate_inputs(self):
        """Validate that at least one input method is provided."""
        if not self.business_objective or not self.business_objective.strip():
            raise ValueError("business_objective is required and cannot be empty")
        self.business_objective = self.business_objective.strip()
        
        has_barcode = self.barcode is not None and self.barcode.strip()
        has_link = self.product_link is not None and self.product_link.strip()
        has_description = self.product_description is not None and self.product_description.strip()
        
        if not (has_barcode or has_link or has_description):
            raise ValueError("At least one of barcode, product_link, or product_description must be provided")
        
        return self


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "name": "API_Final_Agent",
        "version": "1.0.0",
        "status": "ready",
        "description": "Unified service combining ACE_Framework and EssenceAI",
        "endpoints": {
            "run_analysis": "/run-analysis",
            "investigate": "/investigate"
        }
    }


@app.post("/run-analysis")
async def run_analysis(request: UnifiedRequest):
    """
    Run unified analysis using internal ACE and/or Essence pipelines.
    
    No external HTTP calls - all pipelines run internally.
    
    Returns unified JSON with merged results and raw sources.
    """
    # Use provided analysis_id or generate new one
    import time
    start_time = time.time()
    analysis_id = request.analysis_id if request.analysis_id else str(uuid.uuid4())
    
    print(f"🔍 Starting analysis {analysis_id}")
    print(f"   Input: barcode={request.barcode}, link={request.product_link}, desc={bool(request.product_description)}")
    
    ace_result = None
    essence_result = None
    errors = []
    
    # Run ACE pipeline if barcode provided
    if request.barcode:
        try:
            print(f"📦 Running ACE pipeline for barcode: {request.barcode}")
            ace_start = time.time()
            ace_result = await run_ace_analysis(
                barcode=request.barcode,
                business_objective=request.business_objective
            )
            ace_duration = time.time() - ace_start
            print(f"✅ ACE pipeline completed in {ace_duration:.1f}s")
        except Exception as e:
            error_msg = f"ACE pipeline failed: {str(e)}"
            errors.append({"source": "ace", "error": error_msg})
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
    
    # Run Essence pipeline if link or description provided
    if request.product_link or request.product_description:
        try:
            print(f"🌱 Running Essence pipeline")
            essence_start = time.time()
            essence_result = await run_essence_analysis(
                product_link=request.product_link,
                product_description=request.product_description,
                business_objective=request.business_objective,
                domain=request.domain,
                segment=request.segment
            )
            essence_duration = time.time() - essence_start
            print(f"✅ Essence pipeline completed in {essence_duration:.1f}s")
        except Exception as e:
            error_msg = f"Essence pipeline failed: {str(e)}"
            errors.append({"source": "essence", "error": error_msg})
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
    
    total_duration = time.time() - start_time
    print(f"⏱️  Total analysis time: {total_duration:.1f}s")
    
    # Determine status
    ace_ok = ace_result is not None
    essence_ok = essence_result is not None
    
    if ace_ok and essence_ok:
        status = "ok"
    elif ace_ok or essence_ok:
        status = "partial"
    else:
        status = "error"
    
    # Create unified output
    unified_output = create_unified_output(
        analysis_id=analysis_id,
        input_data={
            "business_objective": request.business_objective,
            "barcode": request.barcode,
            "product_link": request.product_link,
            "product_description": request.product_description,
            "domain": request.domain,
            "segment": request.segment
        },
        ace_result=ace_result,
        essence_result=essence_result,
        status=status,
        errors=errors
    )
    
    return unified_output


@app.post("/investigate")
async def investigate():
    """
    Run internal investigation to capture raw outputs from both pipelines.
    Useful for Phase 2 - understanding output structures.
    """
    try:
        results = await investigate_outputs()
        return {
            "status": "ok",
            "message": "Investigation complete. Check artifacts/ directory.",
            "results": results
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Investigation failed: {str(e)}"
        )


if __name__ == "__main__":
    port = int(os.getenv("API_FINAL_AGENT_PORT", "8001"))
    print(f"Starting API_Final_Agent unified service on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
