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

from config import ACEConfig, LLMConfig, PlaybookConfig
from agents import ACEPipeline
from product_data import OpenFoodFactsClient, ImageAnalyzer, NormalizedProductData


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


def run_server(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()