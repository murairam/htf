#!/usr/bin/env python
"""Check if competitor intelligence data is in the database."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketing_analyzer.models import Analysis

# Get the latest analysis
analysis_id = 'f87155cf-df79-4522-8813-1d21d4bbe68b'
analysis = Analysis.objects.filter(analysis_id=analysis_id).first()

if not analysis:
    print(f"❌ Analyse {analysis_id} non trouvée")
    print("\nAnalyses disponibles:")
    for a in Analysis.objects.all().order_by('-created_at')[:5]:
        print(f"  - {a.analysis_id} ({a.created_at})")
    exit(1)

print(f"✅ Analyse trouvée: {analysis_id}")
print(f"   Créée: {analysis.created_at}")

result = analysis.result_data

# Check structure
print("\n📊 Structure des données:")
print(f"   Keys dans result: {list(result.keys())}")

if 'merged' in result:
    print(f"   Keys dans merged: {list(result['merged'].keys())}")
    
    if 'competitor_intelligence' in result['merged']:
        ci = result['merged']['competitor_intelligence']
        print(f"\n✅ competitor_intelligence trouvé!")
        print(f"   Type: {type(ci)}")
        print(f"   Keys: {list(ci.keys()) if isinstance(ci, dict) else 'N/A'}")
        
        if 'ace' in ci:
            ace_data = ci['ace']
            print(f"\n✅ ACE data présent:")
            print(f"   Competitors: {len(ace_data.get('competitors', []))}")
            print(f"   Metrics: {ace_data.get('metrics', {})}")
            print(f"   Visualizations: {'Oui' if 'visualizations' in ace_data else 'Non'}")
        else:
            print("\n❌ ACE data absent de competitor_intelligence")
            
        if 'essence' in ci:
            print(f"\n✅ Essence data présent")
        else:
            print(f"\n⚠️  Essence data absent (normal si pas encore implémenté)")
    else:
        print("\n❌ competitor_intelligence absent de merged")
else:
    print("\n❌ 'merged' absent de result")

print("\n" + "="*60)
