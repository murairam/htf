"""
Temporary EssenceAI API Wrapper
This creates a minimal FastAPI server to expose EssenceAI agents as an API.
This is needed for Phase 1 inspection.

Note: This is a temporary wrapper. In production, EssenceAI should have its own API.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Add essenceAI to path
essenceai_path = Path(__file__).parent.parent / "essenceAI"
sys.path.insert(0, str(essenceai_path))
sys.path.insert(0, str(essenceai_path / "src"))

try:
    from agents.orchestrator import AgentOrchestrator
except ImportError as e:
    print(f"Warning: Could not import EssenceAI agents: {e}")
    print("EssenceAI API wrapper will not work until agents are available.")
    AgentOrchestrator = None

app = FastAPI(title="EssenceAI API Wrapper", version="1.0.0")

# Global orchestrator instance
orchestrator: Optional[AgentOrchestrator] = None


class AnalyzeRequest(BaseModel):
    """Request model for EssenceAI analysis."""
    business_objective: str = ""
    product_link: Optional[str] = None
    product_description: Optional[str] = None
    domain: Optional[str] = None
    segment: Optional[str] = None


def initialize_orchestrator():
    """Initialize the EssenceAI orchestrator."""
    global orchestrator
    
    if orchestrator is not None:
        return orchestrator
    
    if AgentOrchestrator is None:
        raise HTTPException(
            status_code=500,
            detail="EssenceAI agents not available. Check imports."
        )
    
    try:
        data_dir = essenceai_path / "data"
        orchestrator = AgentOrchestrator(data_dir=str(data_dir))
        
        # Initialize research agent
        print("Initializing EssenceAI research agent...")
        orchestrator.initialize_research(force_reload=False)
        print("✅ EssenceAI orchestrator initialized")
        
        return orchestrator
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize EssenceAI orchestrator: {str(e)}"
        )


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "name": "EssenceAI API Wrapper",
        "version": "1.0.0",
        "status": "ready" if orchestrator is not None else "not_initialized"
    }


@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """
    Analyze a product using EssenceAI agents.
    
    Requires either product_link OR product_description.
    
    Note: If EssenceAI agents are not available (missing dependencies),
    returns a mock response for testing purposes.
    """
    # Validate input
    if not request.product_link and not request.product_description:
        raise HTTPException(
            status_code=400,
            detail="Either product_link or product_description is required"
        )
    
    # Check if agents are available
    if AgentOrchestrator is None:
        # Return mock response for testing when agents are not available
        print("⚠️  EssenceAI agents not available, returning mock response")
        return {
            "status": "mock",
            "message": "EssenceAI agents not available (missing dependencies). This is a mock response for testing.",
            "input": {
                "product_link": request.product_link,
                "product_description": request.product_description,
                "business_objective": request.business_objective,
                "domain": request.domain,
                "segment": request.segment
            },
            "mock_data": {
                "competitor_analysis": {
                    "competitors": [
                        {
                            "name": "Mock Competitor 1",
                            "price": "€X.XX",
                            "positioning": "Mock positioning"
                        }
                    ]
                },
                "research_insights": {
                    "insights": [
                        "Mock research insight 1",
                        "Mock research insight 2"
                    ]
                },
                "marketing_strategy": {
                    "recommendations": [
                        "Mock marketing recommendation 1",
                        "Mock marketing recommendation 2"
                    ]
                }
            },
            "workflow": {
                "steps": [
                    {"agent": "competitor", "status": "mock"},
                    {"agent": "research", "status": "mock"},
                    {"agent": "marketing", "status": "mock"}
                ]
            }
        }
    
    # Initialize orchestrator if needed
    try:
        orch = initialize_orchestrator()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initialize orchestrator: {str(e)}"
        )
    
    # Prepare product description
    if request.product_link:
        # For now, use link as description
        # In production, you might want to fetch product info from the link
        product_description = f"Product from link: {request.product_link}"
    else:
        product_description = request.product_description
    
    try:
        # Execute full analysis
        result = orch.execute_full_analysis(
            product_description=product_description,
            domain=request.domain,
            segment=request.segment
        )
        
        # Add business objective to result if provided
        if request.business_objective:
            result["business_objective"] = request.business_objective
        
        # Add input echo
        result["input"] = {
            "product_link": request.product_link,
            "product_description": request.product_description,
            "business_objective": request.business_objective,
            "domain": request.domain,
            "segment": request.segment
        }
        
        return result
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"EssenceAI analysis error: {e}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


if __name__ == "__main__":
    port = int(os.getenv("ESSENCE_API_PORT", "8002"))
    print(f"Starting EssenceAI API wrapper on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)

