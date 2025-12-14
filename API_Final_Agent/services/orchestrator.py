"""
Orchestrator Service
Routes requests to ACE_Framework and/or EssenceAI APIs based on input.
"""

import os
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


class Orchestrator:
    """
    Orchestrates calls to ACE_Framework and EssenceAI APIs.
    """
    
    def __init__(self):
        self.ace_base_url = os.getenv("ACE_BASE_URL", "http://localhost:8001")
        self.essence_base_url = os.getenv("ESSENCE_BASE_URL", "http://localhost:8002")
        self.timeout = int(os.getenv("API_TIMEOUT", "60"))
    
    def call_ace(
        self,
        barcode: str,
        business_objective: str
    ) -> Dict[str, Any]:
        """
        Call ACE_Framework API.
        
        Args:
            barcode: Product barcode
            business_objective: Business objective string
            
        Returns:
            API response as dict, or error dict
        """
        url = f"{self.ace_base_url}/run-analysis"
        analysis_id = str(uuid.uuid4())
        
        payload = {
            "analysis_id": analysis_id,
            "barcode": barcode,
            "objectives": business_objective
        }
        
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return {
                "status": "success",
                "data": response.json()
            }
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "error": "ACE API timeout",
                "data": None
            }
        except requests.exceptions.RequestException as e:
            error_detail = None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = {"status_code": e.response.status_code}
            return {
                "status": "error",
                "error": str(e),
                "error_detail": error_detail,
                "data": None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "data": None
            }
    
    def call_essence(
        self,
        product_link: Optional[str] = None,
        product_description: Optional[str] = None,
        business_objective: str = "",
        domain: Optional[str] = None,
        segment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Call EssenceAI API.
        
        Args:
            product_link: Optional product URL
            product_description: Optional product description
            business_objective: Business objective string
            domain: Optional domain filter
            segment: Optional segment filter
            
        Returns:
            API response as dict, or error dict
        """
        url = f"{self.essence_base_url}/analyze"
        
        payload = {
            "business_objective": business_objective
        }
        
        if product_link:
            payload["product_link"] = product_link
        elif product_description:
            payload["product_description"] = product_description
        else:
            return {
                "status": "error",
                "error": "Either product_link or product_description is required",
                "data": None
            }
        
        if domain:
            payload["domain"] = domain
        if segment:
            payload["segment"] = segment
        
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return {
                "status": "success",
                "data": response.json()
            }
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "error": "EssenceAI API timeout",
                "data": None
            }
        except requests.exceptions.RequestException as e:
            error_detail = None
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = {"status_code": e.response.status_code}
            return {
                "status": "error",
                "error": str(e),
                "error_detail": error_detail,
                "data": None
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "data": None
            }
    
    def orchestrate(
        self,
        business_objective: str,
        barcode: Optional[str] = None,
        product_link: Optional[str] = None,
        product_description: Optional[str] = None,
        domain: Optional[str] = None,
        segment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate calls to ACE and/or EssenceAI based on provided inputs.
        
        Returns:
            Dict with ace_result and essence_result keys
        """
        results = {
            "ace_result": None,
            "essence_result": None
        }
        
        # Call ACE if barcode provided
        if barcode:
            print(f"📞 Calling ACE API for barcode: {barcode}")
            results["ace_result"] = self.call_ace(barcode, business_objective)
        
        # Call EssenceAI if link or description provided
        if product_link or product_description:
            print(f"📞 Calling EssenceAI API")
            results["essence_result"] = self.call_essence(
                product_link=product_link,
                product_description=product_description,
                business_objective=business_objective,
                domain=domain,
                segment=segment
            )
        
        return results

