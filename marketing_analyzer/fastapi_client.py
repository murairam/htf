import requests
import logging
from typing import Tuple, Union
from django.conf import settings

logger = logging.getLogger(__name__)


class FastAPIClient:
    """Client for communicating with the FastAPI LLM analysis service."""
    
    def __init__(self):
        self.base_url = settings.FASTAPI_URL
        self.timeout = settings.FASTAPI_TIMEOUT
    
    def run_analysis(self, analysis_id: str, barcode: str, objectives: str) -> Tuple[bool, Union[dict, str]]:
        """
        Run complete LLM analysis on product.
        
        FastAPI will:
        1. Lookup product from OpenFoodFacts using barcode
        2. Extract image_front_url from OpenFoodFacts response
        3. Run LLM analysis
        4. Return complete JSON with scores, recommendations, and image_front_url
        
        Args:
            analysis_id: Unique analysis identifier
            barcode: Product barcode (EAN/UPC)
            objectives: Business objectives for the analysis
            
        Returns:
            Tuple of (success: bool, result: dict or error_message: str)
        """
        url = f"{self.base_url}/run-analysis"
        
        payload = {
            'analysis_id': analysis_id,
            'barcode': barcode,
            'objectives': objectives
        }
        
        try:
            logger.info(f"Calling FastAPI /run-analysis for analysis_id={analysis_id}, barcode={barcode}")
            
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                logger.info(f"FastAPI analysis successful for {analysis_id}")
                return True, response.json()
            elif response.status_code == 404:
                logger.warning(f"Product not found: {barcode}")
                return False, "Product not found in our database. Please check the barcode."
            elif response.status_code == 500:
                logger.error(f"FastAPI internal error for {analysis_id}")
                return False, "Analysis service encountered an error. Please try again."
            else:
                logger.error(f"Unexpected status {response.status_code} from FastAPI")
                return False, f"Unexpected error (status {response.status_code}). Please try again."
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling FastAPI for analysis {analysis_id}")
            return False, "Analysis is taking too long. Please try again later."
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error to FastAPI: {url}")
            return False, "Analysis service is currently unavailable. Please try again later."
        except Exception as e:
            logger.exception(f"Unexpected error calling FastAPI: {e}")
            return False, "An unexpected error occurred. Please try again."
    
    def health_check(self) -> bool:
        """Check if FastAPI service is available."""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False
