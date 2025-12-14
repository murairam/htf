"""
ACE Pipeline Runner
Runs ACE_Framework pipeline internally (no HTTP calls).
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Import ACE components using relative imports
from ..ace.config import ACEConfig, LLMConfig
from ..ace.agents import ACEPipeline
from ..ace.product_data import OpenFoodFactsClient, ImageAnalyzer
from ..ace.competitor_data import get_competitor_intelligence
from ..ace.marketing_strategy import generate_marketing_strategy
from ..ace.research_insights import generate_research_insights
from ..utils.json_serializer import make_json_serializable


# Global state for ACE pipeline
_ace_pipeline: Optional[ACEPipeline] = None
_ace_image_analyzer: Optional[ImageAnalyzer] = None
_ace_off_client = OpenFoodFactsClient()


def _initialize_ace_pipeline():
    """Initialize ACE pipeline if not already initialized."""
    global _ace_pipeline, _ace_image_analyzer
    
    if _ace_pipeline is not None:
        return
    
    # Get API key - try BLACKBOX first, then OpenAI for backward compatibility
    api_key = os.getenv("BLACKBOX_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("BLACKBOX_API_KEY or OPENAI_API_KEY environment variable is required for ACE pipeline")
    
    # Initialize pipeline
    llm_config = LLMConfig(api_key=api_key)
    ace_config = ACEConfig(llm=llm_config)
    _ace_pipeline = ACEPipeline(ace_config)
    
    # Initialize image analyzer
    _ace_image_analyzer = ImageAnalyzer(api_key=api_key)
    
    provider = "BLACKBOX" if os.getenv("BLACKBOX_API_KEY") else "OpenAI"
    print(f"✅ ACE pipeline initialized with {provider}")


async def run_ace_analysis(
    barcode: str,
    business_objective: str
) -> Dict[str, Any]:
    """
    Run ACE pipeline analysis internally.
    
    Args:
        barcode: Product barcode
        business_objective: Business objective string
        
    Returns:
        Complete ACE analysis result as dict
    """
    # Initialize if needed
    import time
    init_start = time.time()
    _initialize_ace_pipeline()
    init_duration = time.time() - init_start
    if init_duration > 1:
        print(f"   ACE pipeline initialization took {init_duration:.1f}s")
    
    # 1. Lookup product from OpenFoodFacts
    print(f"   Looking up product from OpenFoodFacts...")
    off_start = time.time()
    product = _ace_off_client.get_product_by_barcode(barcode)
    off_duration = time.time() - off_start
    print(f"   OpenFoodFacts lookup completed in {off_duration:.1f}s")
    
    if not product:
        raise ValueError(f"Product not found for barcode: {barcode}")
    
    # 2. Analyze image if available
    image_analysis = {}
    if product.image_front_url and _ace_image_analyzer:
        try:
            print(f"   Analyzing product image...")
            image_start = time.time()
            image_result = _ace_image_analyzer.analyze_from_url(product.image_front_url)
            image_analysis = image_result.to_dict()
            image_duration = time.time() - image_start
            print(f"   Image analysis completed in {image_duration:.1f}s")
        except Exception as e:
            print(f"⚠️  Image analysis failed: {e}")
            print(f"   Continuing without image analysis...")
            # Continue without image analysis - this is not critical
            image_analysis = {}
    
    # 3. Run ACE pipeline
    print(f"   Running ACE pipeline (this may take 30-120 seconds for LLM processing)...")
    pipeline_start = time.time()
    
    # Serialize product data to ensure JSON compatibility
    product_data_dict = make_json_serializable(product)
    
    pipeline_result = _ace_pipeline.run(
        product_data=product_data_dict,
        image_analysis=image_analysis,
        business_objective=business_objective,
        feedback=None
    )
    pipeline_duration = time.time() - pipeline_start
    print(f"   ✅ ACE pipeline.run() completed in {pipeline_duration:.1f}s")
    
    # 4. Extract results
    if hasattr(pipeline_result, 'to_dict'):
        result_dict = pipeline_result.to_dict()
        generator_output = result_dict.get("generator_output", {})
        reflector_output = result_dict.get("reflector_output", {})
    else:
        generator_output = pipeline_result if isinstance(pipeline_result, dict) else {}
        reflector_output = {}
    
    # 5. Serialize product data to ensure all nested objects are JSON-compatible
    product_serialized = make_json_serializable(product)
    
    # 6. Get competitor intelligence data
    print(f"   Generating competitor intelligence...")
    competitor_start = time.time()
    competitor_intelligence = get_competitor_intelligence(
        product_category=product_data_dict.get('plant_based_category', 'plant-based-burger')
    )
    competitor_duration = time.time() - competitor_start
    print(f"   ✅ Competitor intelligence generated in {competitor_duration:.1f}s")
    
    # 7. Generate marketing strategy
    print(f"   Generating marketing strategy...")
    marketing_start = time.time()
    marketing_strategy = generate_marketing_strategy(
        product_data=product_serialized,
        scoring_results=generator_output.get("scores", {}),
        competitor_intelligence=competitor_intelligence,
        business_objective=business_objective
    )
    marketing_duration = time.time() - marketing_start
    print(f"   ✅ Marketing strategy generated in {marketing_duration:.1f}s")
    
    # 8. Generate research insights
    print(f"   Generating research insights...")
    research_start = time.time()
    research_insights = generate_research_insights(
        product_data=product_serialized,
        scoring_results=generator_output,
        competitor_intelligence=competitor_intelligence,
        marketing_strategy=marketing_strategy
    )
    research_duration = time.time() - research_start
    print(f"   ✅ Research insights generated in {research_duration:.1f}s")
    
    # 9. Build complete result (similar to old api.py format)
    from datetime import datetime
    import re
    
    def _format_key_insights(key_insights):
        """Format key_insights from string to list."""
        if not key_insights:
            return []
        if isinstance(key_insights, list):
            return key_insights
        if isinstance(key_insights, str):
            if '\n' in key_insights:
                lines = [line.strip() for line in key_insights.split('\n') if line.strip() and not line.strip().startswith('#')]
                cleaned = []
                for line in lines:
                    line = line.lstrip('0123456789.-) ')
                    line = line.lstrip('•-* ')
                    if line:
                        cleaned.append(line)
                return cleaned if cleaned else [key_insights]
            return [key_insights]
        return []
    
    result = {
        "export_metadata": {
            "export_date": datetime.now().isoformat(),
            "export_type": "ACE Plant-Based Product Intelligence - Complete Report",
            "version": "1.0.0"
        },
        "business_objective": {
            "objective_key": generator_output.get("objective", ""),
            "objective_description": business_objective if business_objective else generator_output.get("objective", ""),
            "scoring_weights": {}
        },
        "product_information": {
            "basic_info": {
                "name": product_serialized.get('name'),
                "brand": product_serialized.get('brand'),
                "product_id": barcode,
                "category": product_serialized.get('plant_based_category')
            },
            "ingredients": {
                "ingredients_text": product_serialized.get('ingredients_text'),
                "ingredients_count": len(product_serialized.get('ingredients', [])),
                "additives_count": product_serialized.get('additives_count', 0)
            },
            "nutrition": {
                "nova_group": product_serialized.get('nova_group'),
                "nutriscore": product_serialized.get('nutriscore'),
                "nutriments": product_serialized.get('nutriments', {})
            },
            "labels_certifications": product_serialized.get('labels', []),
            "packaging": product_serialized.get('packaging', {}),
            "origin": product_serialized.get('origin', ""),
            "countries": product_serialized.get('countries', [])
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
            "key_insights": _format_key_insights(reflector_output.get("key_insights", "")) if reflector_output else [],
            "improvement_guidelines": reflector_output.get("improved_reasoning_guidelines", "") if reflector_output else ""
        },
        "barcode": barcode,
        "objectives": business_objective,
        "image_front_url": product_serialized.get('image_front_url'),
        "competitor_intelligence": competitor_intelligence,
        "marketing_strategy": marketing_strategy,
        "research_insights": research_insights
    }
    
    return result

