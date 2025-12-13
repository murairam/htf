#!/usr/bin/env python3
"""
Update Django template with correct Vite build asset filenames.
Reads from frontend/dist/.vite/manifest.json and updates marketing_analyzer/templates/index.html
"""
import json
import re
from pathlib import Path

def update_template():
    # Paths
    manifest_path = Path(__file__).parent / 'frontend' / 'dist' / '.vite' / 'manifest.json'
    template_path = Path(__file__).parent / 'marketing_analyzer' / 'templates' / 'index.html'
    
    # Read manifest
    if not manifest_path.exists():
        print(f"❌ Manifest not found: {manifest_path}")
        print("   Run 'cd frontend && npm run build' first")
        return False
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    # Extract asset filenames
    index_entry = manifest.get('index.html', {})
    css_file = index_entry.get('css', [None])[0]
    js_file = index_entry.get('file')
    
    if not css_file or not js_file:
        print(f"❌ Could not find asset files in manifest")
        print(f"   CSS: {css_file}")
        print(f"   JS: {js_file}")
        return False
    
    # Remove 'assets/' prefix if present (manifest includes it)
    if css_file.startswith('assets/'):
        css_file = css_file[7:]  # Remove 'assets/'
    if js_file.startswith('assets/'):
        js_file = js_file[7:]  # Remove 'assets/'
    
    print(f"📦 Found assets:")
    print(f"   CSS: {css_file}")
    print(f"   JS: {js_file}")
    
    # Read template
    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        return False
    
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    # Update CSS reference
    template_content = re.sub(
        r'{% static \'react/assets/index-[^\']+\.css\' %}',
        f"{{% static 'react/assets/{css_file}' %}}",
        template_content
    )
    
    # Update JS reference
    template_content = re.sub(
        r'{% static \'react/assets/index-[^\']+\.js\' %}',
        f"{{% static 'react/assets/{js_file}' %}}",
        template_content
    )
    
    # Write updated template
    with open(template_path, 'w') as f:
        f.write(template_content)
    
    print(f"✅ Template updated: {template_path}")
    return True

if __name__ == '__main__':
    success = update_template()
    exit(0 if success else 1)
