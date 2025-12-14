"""
JSON Serialization Helper
Converts Pydantic models and other objects to JSON-serializable format
"""

from typing import Any, Dict, List
from datetime import datetime, date
from enum import Enum


def make_json_serializable(obj: Any) -> Any:
    """
    Convert any object to JSON-serializable format.
    
    Handles:
    - Pydantic v2 models (model_dump)
    - Pydantic v1 models (dict)
    - Objects with to_dict()
    - Objects with __dict__
    - Lists, tuples, sets
    - Dictionaries
    - Datetime objects
    - Enums
    - Primitives
    
    Args:
        obj: Object to convert
        
    Returns:
        JSON-serializable version of the object
    """
    # None, bool, int, float, str are already serializable
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    
    # Datetime objects
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    
    # Enums
    if isinstance(obj, Enum):
        return obj.value
    
    # Pydantic v2 models
    if hasattr(obj, 'model_dump'):
        try:
            return obj.model_dump()
        except Exception:
            pass
    
    # Pydantic v1 models
    if hasattr(obj, 'dict') and callable(obj.dict):
        try:
            return obj.dict()
        except Exception:
            pass
    
    # Objects with to_dict method
    if hasattr(obj, 'to_dict') and callable(obj.to_dict):
        try:
            result = obj.to_dict()
            # Recursively serialize the result
            return make_json_serializable(result)
        except Exception:
            pass
    
    # Lists, tuples, sets
    if isinstance(obj, (list, tuple, set)):
        return [make_json_serializable(item) for item in obj]
    
    # Dictionaries
    if isinstance(obj, dict):
        return {
            str(key): make_json_serializable(value) 
            for key, value in obj.items()
        }
    
    # Objects with __dict__
    if hasattr(obj, '__dict__'):
        try:
            return {
                key: make_json_serializable(value)
                for key, value in obj.__dict__.items()
                if not key.startswith('_')  # Skip private attributes
            }
        except Exception:
            pass
    
    # Last resort: convert to string
    try:
        return str(obj)
    except Exception:
        return f"<non-serializable: {type(obj).__name__}>"


def safe_json_dump(obj: Any) -> Dict[str, Any]:
    """
    Safely convert an object to a JSON-serializable dictionary.
    
    This is a convenience wrapper around make_json_serializable
    that ensures the result is always a dictionary.
    
    Args:
        obj: Object to convert
        
    Returns:
        JSON-serializable dictionary
    """
    result = make_json_serializable(obj)
    
    if isinstance(result, dict):
        return result
    else:
        return {"value": result}
