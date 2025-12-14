"""
Script to fix imports in copied ACE and Essence files.
"""

import re
from pathlib import Path

def fix_ace_imports(file_path: Path):
    """Fix imports in ACE files."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix relative imports
    replacements = [
        (r'^from config import', 'from .config import'),
        (r'^from llm_client import', 'from .llm_client import'),
        (r'^from playbook import', 'from .playbook import'),
        (r'^from product_data import', 'from .product_data import'),
        (r'^from agents import', 'from .agents import'),
        (r'^from prompts import', 'from .prompts import'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def fix_essence_imports(file_path: Path):
    """Fix imports in Essence files."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove sys.path manipulations that are no longer needed
    content = re.sub(r'sys\.path\.append\([^)]+\)\n', '', content)
    content = re.sub(r'sys\.path\.insert\([^)]+\)\n', '', content)
    
    # Fix relative imports
    replacements = [
        (r'^from agents\.', 'from .agents.'),
        (r'^from rag_engine', 'from .rag_engine'),
        (r'^from competitor_data', 'from .competitor_data'),
        (r'^from product_parser', 'from .product_parser'),
        (r'^from database', 'from .database'),
        (r'^from blackbox_client', 'from .blackbox_client'),
        (r'^from logger', 'from .logger'),
        (r'^from rate_limited_embedding', 'from .rate_limited_embedding'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    ace_dir = Path(__file__).parent / "api_final_agent" / "ace"
    essence_dir = Path(__file__).parent / "api_final_agent" / "essence"
    
    # Fix ACE imports
    for py_file in ace_dir.glob("*.py"):
        if py_file.name != "__init__.py":
            print(f"Fixing imports in {py_file}")
            fix_ace_imports(py_file)
    
    # Fix Essence imports
    for py_file in essence_dir.rglob("*.py"):
        if py_file.name != "__init__.py":
            print(f"Fixing imports in {py_file}")
            fix_essence_imports(py_file)
    
    print("✅ All imports fixed!")

