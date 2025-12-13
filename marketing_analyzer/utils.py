import json
import os
from pathlib import Path
from django.conf import settings


def load_static_result(analysis_id):
    """
    Load a static JSON result file based on analysis_id.
    Uses modulo operation to select from available example files.
    """
    # Convert UUID to integer for modulo operation
    id_hash = hash(str(analysis_id))
    file_index = abs(id_hash) % 3  # We have 3 example files
    
    # Map to example files
    example_files = [
        'example_1.json',
        'example_2.json',
        'example_3.json'
    ]
    
    filename = example_files[file_index]
    file_path = Path(__file__).parent / 'static_results' / filename
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Update analysis_id in the loaded data
            data['analysis_id'] = str(analysis_id)
            return data
    except FileNotFoundError:
        raise Exception(f"Static result file not found: {filename}")
    except json.JSONDecodeError:
        raise Exception(f"Invalid JSON in file: {filename}")
