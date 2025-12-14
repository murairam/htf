"""
FastAPI Backend for ACE Plant-Based Packaging Intelligence.

REST API for product analysis. Internal processes are hidden from users.
"""
import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from . import config as config_module
from .config import ACEConfig, LLMConfig, PlaybookConfig
from .agents import ACEPipeline
from .product_data import OpenFoodFactsClient, ImageAnalyzer, NormalizedProductData


class LLMConfigRequest(BaseModel):
    provider: str = "openai"
    model: str = "gpt-4o"
    temperature: float = 0.0
    api_key: Optional[str] = None


class InitializeRequest(BaseModel):
    llm_config: LLMConfigRequest = Field(default_factory=LLMConfigRequest)


class AnalysisRequest(BaseModel):
    product_data: Dict[str, Any]
    image_analysis: Dict[str, Any] = Field(default_factory=dict)
    business_objective: str


class BarcodeRequest(BaseModel):
    barcode: str
    analyze_image: bool = True


class AppState:
    def __init__(self):
        self.pipeline: Optional[ACEPipeline] = None
        self.image_analyzer: Optional[ImageAnalyzer] = None
        self.initialized: bool = False
        self.off_client = OpenFoodFactsClient()
    
    def initialize(self, config: ACEConfig, api_key: str = None):
        self.pipeline = ACEPipeline(config)
        self.image_analyzer = ImageAnalyzer(api_key=api_key)
        self.initialized = True
    
    @staticmethod
    def _format_key_insights(key_insights):
        """Format key_insights from string to list if needed."""
        if not key_insights:
            return []
        if isinstance(key_insights, list):
            return key_insights
        if isinstance(key_insights, str):
            # The Reflector returns key_insights as a string, but we need a list
            # Try to split by newlines, bullets, or numbered items
            if '\n' in key_insights:
                # Split by newlines and clean up
                lines = [line.strip() for line in key_insights.split('\n') if line.strip() and not line.strip().startswith('#')]
                # Remove common prefixes like "1.", "2.", "-", "•"
                cleaned = []
                for line in lines:
                    # Remove numbered prefixes
                    line = line.lstrip('0123456789.-) ')
                    # Remove bullet points
                    line = line.lstrip('•-* ')
                    if line:
                        cleaned.append(line)
                return cleaned if cleaned else [key_insights]
            # If it's a single string without newlines, return as list with one item
            return [key_insights]
        return []


app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Plant-Based Packaging Intelligence API starting...")
    yield
    print("API shutting down...")


app = FastAPI(title="Plant-Based Packaging Intelligence API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/")
async def root():
    return {"name": "Plant-Based Packaging Intelligence API", "version": "1.0.0", "initialized": app_state.initialized}


@app.post("/initialize")
async def initialize(request: InitializeRequest):
    try:
        llm_config = LLMConfig(provider=request.llm_config.provider, model=request.llm_config.model,
                               temperature=request.llm_config.temperature, api_key=request.llm_config.api_key)
        app_state.initialize(ACEConfig(llm=llm_config), api_key=request.llm_config.api_key)
        return {"status": "initialized"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/product/lookup")
async def lookup_product(request: BarcodeRequest):
    product = app_state.off_client.get_product_by_barcode(request.barcode)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    result = {"product_data": product.to_dict()}
    
    if request.analyze_image and product.image_front_url and app_state.image_analyzer:
        image_result = app_state.image_analyzer.analyze_from_url(product.image_front_url)
        result["image_analysis"] = image_result.to_dict()
    
    return result


@app.post("/analyze")
async def analyze_product(request: AnalysisRequest):
    if not app_state.initialized:
        raise HTTPException(status_code=400, detail="Not initialized")
    
    try:
        # Returns sanitized user-facing output only
        result = app_state.pipeline.analyze(
            product_data=request.product_data,
            image_analysis=request.image_analysis,
            business_objective=request.business_objective
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class RunAnalysisRequest(BaseModel):
    """Request for complete analysis from barcode."""
    analysis_id: str
    barcode: str
    objectives: str = ""  # Optional - empty string if not provided


@app.post("/run-analysis")
async def run_analysis(request: RunAnalysisRequest):
    """
    Complete analysis endpoint for Django integration.
    
    1. Lookup product from OpenFoodFacts
    2. Analyze image if available
    3. Run ACE pipeline analysis
    4. Return complete JSON with all results
    """
    import os
    import traceback
    
    try:
        # 1. Lookup product
        product = app_state.off_client.get_product_by_barcode(request.barcode)
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product not found in our database. Please check the barcode."
            )
        
        # 2. Analyze image if available
        image_analysis = {}
        if product.image_front_url and app_state.image_analyzer:
            try:
                image_result = app_state.image_analyzer.analyze_from_url(product.image_front_url)
                image_analysis = image_result.to_dict()
            except Exception as e:
                print(f"Image analysis failed: {e}")
                # Continue without image analysis
        
        # 3. Initialize pipeline if needed
        if not app_state.initialized:
            # Auto-initialize with default config
            from config import ACEConfig, LLMConfig
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise HTTPException(
                    status_code=500,
                    detail="OPENAI_API_KEY environment variable is not set. Please set it before running the analysis."
                )
            
            try:
                llm_config = LLMConfig(api_key=api_key)
                app_state.initialize(ACEConfig(llm=llm_config), api_key=api_key)
            except Exception as init_error:
                error_trace = traceback.format_exc()
                print(f"Pipeline initialization error: {init_error}")
                print(f"Traceback: {error_trace}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to initialize analysis pipeline: {str(init_error)}"
                )
        
        # 4. Run analysis
        # Use objectives if provided, otherwise use empty string
        business_objective = request.objectives if request.objectives else ""
        
        try:
            # Use pipeline.run() to get complete analysis including Reflector (quality_insights)
            # This is slower but provides complete data including quality_insights
            pipeline_result = app_state.pipeline.run(
                product_data=product.to_dict(),
                image_analysis=image_analysis,
                business_objective=business_objective,
                feedback=None
            )
            
            # Extract generator and reflector outputs
            if hasattr(pipeline_result, 'to_dict'):
                result_dict = pipeline_result.to_dict()
                generator_output = result_dict.get("generator_output", {})
                reflector_output = result_dict.get("reflector_output", {})
            else:
                # Fallback if result is not in expected format
                generator_output = pipeline_result if isinstance(pipeline_result, dict) else {}
                reflector_output = {}
                
        except Exception as analyze_error:
            error_trace = traceback.format_exc()
            print(f"Analysis execution error: {analyze_error}")
            print(f"Traceback: {error_trace}")
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {str(analyze_error)}"
            )
        
        # 5. Transform pipeline result to new format structure
        
        # Build the complete result in the new format
        result = {
            "export_metadata": {
                "export_date": datetime.now().isoformat(),
                "export_type": "ACE Plant-Based Product Intelligence - Complete Report",
                "version": "1.0.0"
            },
            "business_objective": {
                "objective_key": generator_output.get("objective", ""),
                "objective_description": business_objective if business_objective else generator_output.get("objective", ""),
                "scoring_weights": {}  # Will be calculated based on objective
            },
            "product_information": {
                "basic_info": {
                    "name": product.name,
                    "brand": product.brand,
                    "product_id": request.barcode,
                    "category": product.plant_based_category
                },
                "ingredients": {
                    "ingredients_text": product.ingredients_text,
                    "ingredients_count": len(product.ingredients) if hasattr(product, 'ingredients') else 0,
                    "additives_count": product.additives_count if hasattr(product, 'additives_count') else 0
                },
                "nutrition": {
                    "nova_group": product.nova_group if hasattr(product, 'nova_group') else None,
                    "nutriscore": product.nutriscore if hasattr(product, 'nutriscore') else None,
                    "nutriments": {}
                },
                "labels_certifications": product.labels if hasattr(product, 'labels') else [],
                "packaging": {
                    "materials": product.packaging.materials if hasattr(product, 'packaging') and hasattr(product.packaging, 'materials') else [],
                    "recyclable": product.packaging.recyclable if hasattr(product, 'packaging') and hasattr(product.packaging, 'recyclable') else False
                },
                "origin": "",
                "countries": []
            },
            "image_analysis": image_analysis if image_analysis else {},
            "scoring_results": {
                "confidence_level": generator_output.get("confidence", "medium"),
                "scores": {
                    "attractiveness_score": generator_output.get("scores", {}).get("attractiveness_score", 0),
                    "utility_score": generator_output.get("scores", {}).get("utility_score", 0),
                    "positioning_score": generator_output.get("scores", {}).get("positioning_score", 0),
                    "global_score": generator_output.get("scores", {}).get("global_score", 0)
                },
                "criteria_breakdown": generator_output.get("criteria", {})
            },
            "evidence_based_explanations": generator_output.get("explanations", {}),
            "swot_analysis": {
                "strengths": generator_output.get("analysis", {}).get("strengths", []),
                "weaknesses": generator_output.get("analysis", {}).get("weaknesses", []),
                "risks": generator_output.get("analysis", {}).get("risks", [])
            },
            "packaging_improvement_proposals": generator_output.get("packaging_improvement_proposals", []),
            "go_to_market_strategy": {
                "shelf_positioning": generator_output.get("go_to_market_recommendations", {}).get("shelf_positioning", ""),
                "b2b_targeting": generator_output.get("go_to_market_recommendations", {}).get("b2b_targeting", ""),
                "regional_relevance": generator_output.get("go_to_market_recommendations", {}).get("regional_relevance", "")
            },
            "quality_insights": {
                "reflector_analysis": reflector_output.get("analysis", "") if reflector_output else "",
                "key_insights": AppState._format_key_insights(reflector_output.get("key_insights", "")) if reflector_output else [],
                "improvement_guidelines": reflector_output.get("improved_reasoning_guidelines", "") if reflector_output else ""
            },
            # Keep metadata for compatibility
            "analysis_id": request.analysis_id,
            "barcode": request.barcode,
            "objectives": request.objectives,
            "image_front_url": product.image_front_url
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Unexpected error in run_analysis: {e}")
        print(f"Traceback: {error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )


def run_server(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()