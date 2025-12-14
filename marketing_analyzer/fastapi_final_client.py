"""
Client for API_Final_Agent unified orchestrator.
Replaces the old FastAPIClient that called ACE directly.
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)


class APIFinalAgentClient:
    """
    Client for API_Final_Agent unified orchestrator service.
    """
    
    def __init__(self):
        from django.conf import settings
        self.base_url = getattr(settings, 'FINAL_AGENT_BASE_URL', 'http://localhost:8001')
        self.timeout = int(getattr(settings, 'FINAL_AGENT_TIMEOUT', 60))
    
    def run_analysis(
        self,
        analysis_id: str,
        business_objective: str,
        barcode: str = None,
        product_link: str = None,
        product_description: str = None,
        domain: str = None,
        segment: str = None
    ) -> tuple[bool, dict]:
        """
        Call API_Final_Agent /run-analysis endpoint.
        
        Args:
            analysis_id: Django analysis ID
            business_objective: Required business objective
            barcode: Optional barcode for ACE API
            product_link: Optional product URL for EssenceAI
            product_description: Optional product description for EssenceAI
            domain: Optional domain filter
            segment: Optional segment filter
            
        Returns:
            Tuple of (success: bool, result: dict)
            If success=False, result contains error message
        """
        url = f"{self.base_url}/run-analysis"
        
        payload = {
            "analysis_id": analysis_id,
            "business_objective": business_objective
        }
        
        # Add optional fields
        if barcode:
            payload["barcode"] = barcode
        if product_link:
            payload["product_link"] = product_link
        if product_description:
            payload["product_description"] = product_description
        if domain:
            payload["domain"] = domain
        if segment:
            payload["segment"] = segment
        
        try:
            logger.info(f"Calling API_Final_Agent: {url} (timeout: {self.timeout}s)")
            logger.debug(f"Payload: {payload}")
            
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"API_Final_Agent analysis successful: {analysis_id}")
                return True, result
            else:
                error_detail = response.json() if response.content else {"detail": "Unknown error"}
                error_msg = error_detail.get("detail", f"HTTP {response.status_code}")
                logger.error(f"API_Final_Agent error: {error_msg}")
                return False, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = f"API_Final_Agent timeout after {self.timeout}s"
            logger.error(error_msg)
            return False, error_msg
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API_Final_Agent request failed: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error calling API_Final_Agent: {str(e)}"
            logger.exception(error_msg)
            return False, error_msg

