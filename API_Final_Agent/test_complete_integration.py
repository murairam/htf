"""
Test complet pour vérifier l'intégration API_FINAL_AGENT
Vérifie que essenceAI + ACE_Framework fonctionnent correctement ensemble
"""

import os
import sys
import json
from pathlib import Path
import asyncio

# Load .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded .env from {env_path}")
else:
    print(f"⚠️  .env not found at {env_path}")

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from api_final_agent.pipelines.ace_pipeline import run_ace_analysis
from api_final_agent.pipelines.essence_pipeline import run_essence_analysis
from api_final_agent.unified_output import create_unified_output


async def test_essence_pipeline():
    """Test essenceAI pipeline avec les PDFs"""
    print("\n" + "="*80)
    print("TEST 1: EssenceAI Pipeline (avec PDFs)")
    print("="*80)
    
    try:
        result = await run_essence_analysis(
            product_description="Plant-based chocolate spread made from hazelnuts and cocoa",
            business_objective="Increase market share in flexitarian segment",
            domain="Plant-Based",
            segment="Flexitarian"
        )
        
        print("\n✅ EssenceAI pipeline completed!")
        print(f"Status: {result.get('status', 'unknown')}")
        
        # Check for key components
        checks = {
            "competitor_analysis": "competitor_analysis" in result or ("mock_data" in result and "competitor_analysis" in result["mock_data"]),
            "research_insights": "research_insights" in result or ("mock_data" in result and "research_insights" in result["mock_data"]),
            "marketing_strategy": "marketing_strategy" in result or ("mock_data" in result and "marketing_strategy" in result["mock_data"]),
            "workflow": "workflow" in result
        }
        
        print("\nComponents présents:")
        for component, present in checks.items():
            status = "✅" if present else "❌"
            print(f"  {status} {component}")
        
        # Save result
        output_file = Path(__file__).parent / "artifacts" / "test_essence_output.json"
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n📁 Résultat sauvegardé: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Erreur dans essenceAI pipeline: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_ace_pipeline():
    """Test ACE_Framework pipeline"""
    print("\n" + "="*80)
    print("TEST 2: ACE_Framework Pipeline")
    print("="*80)
    
    try:
        result = await run_ace_analysis(
            barcode="3017620422003",  # Nutella
            business_objective="Increase flexitarian appeal"
        )
        
        print("\n✅ ACE pipeline completed!")
        
        # Check for key components
        checks = {
            "product_information": "product_information" in result,
            "scoring_results": "scoring_results" in result,
            "swot_analysis": "swot_analysis" in result,
            "image_analysis": "image_analysis" in result,
            "packaging_improvements": "packaging_improvement_proposals" in result,
            "go_to_market_strategy": "go_to_market_strategy" in result
        }
        
        print("\nComponents présents:")
        for component, present in checks.items():
            status = "✅" if present else "❌"
            print(f"  {status} {component}")
        
        # Save result
        output_file = Path(__file__).parent / "artifacts" / "test_ace_output.json"
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n📁 Résultat sauvegardé: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Erreur dans ACE pipeline: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_unified_output():
    """Test la sortie unifiée combinant ACE + Essence"""
    print("\n" + "="*80)
    print("TEST 3: Unified Output (ACE + EssenceAI)")
    print("="*80)
    
    try:
        # Run both pipelines
        print("\n🔄 Exécution des deux pipelines...")
        
        ace_result = await run_ace_analysis(
            barcode="3017620422003",
            business_objective="Comprehensive market analysis"
        )
        
        essence_result = await run_essence_analysis(
            product_description="Chocolate hazelnut spread",
            business_objective="Comprehensive market analysis",
            domain="Plant-Based",
            segment="Flexitarian"
        )
        
        # Create unified output
        print("\n🔄 Création de la sortie unifiée...")
        unified = create_unified_output(
            analysis_id="test-unified-001",
            input_data={
                "business_objective": "Comprehensive market analysis",
                "barcode": "3017620422003",
                "product_description": "Chocolate hazelnut spread",
                "domain": "Plant-Based",
                "segment": "Flexitarian"
            },
            ace_result=ace_result,
            essence_result=essence_result,
            status="ok",
            errors=[]
        )
        
        print("\n✅ Unified output créé!")
        
        # Check merged components
        merged = unified.get('merged', {})
        checks = {
            "product_information": "product_information" in merged,
            "scoring_results": "scoring_results" in merged,
            "swot_analysis": "swot_analysis" in merged,
            "competitor_analysis": "competitor_analysis" in merged,
            "research_insights": "research_insights" in merged,
            "marketing_strategy": "marketing_strategy" in merged,
            "visuals": "visuals" in merged,
            "raw_sources.ace": unified.get('raw_sources', {}).get('ace') is not None,
            "raw_sources.essence": unified.get('raw_sources', {}).get('essence') is not None
        }
        
        print("\nComponents dans merged:")
        for component, present in checks.items():
            status = "✅" if present else "❌"
            print(f"  {status} {component}")
        
        # Check visualizations
        visuals = merged.get('visuals', [])
        print(f"\n📊 Visualisations générées: {len(visuals)}")
        for i, visual in enumerate(visuals, 1):
            print(f"  {i}. {visual.get('title', 'Unknown')} ({visual.get('type', 'unknown')})")
        
        # Save unified result
        output_file = Path(__file__).parent / "artifacts" / "test_unified_output.json"
        output_file.parent.mkdir(exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unified, f, indent=2, ensure_ascii=False)
        print(f"\n📁 Résultat unifié sauvegardé: {output_file}")
        
        return unified
        
    except Exception as e:
        print(f"\n❌ Erreur dans unified output: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_pdf_access():
    """Test l'accès aux PDFs dans essenceAI"""
    print("\n" + "="*80)
    print("TEST 4: Vérification des PDFs")
    print("="*80)
    
    data_dir = Path(__file__).parent / "api_final_agent" / "essence" / "data"
    
    print(f"\n📁 Répertoire data: {data_dir}")
    print(f"   Existe: {'✅' if data_dir.exists() else '❌'}")
    
    if data_dir.exists():
        pdf_files = list(data_dir.glob("*.pdf"))
        print(f"\n📄 PDFs trouvés: {len(pdf_files)}")
        for pdf in pdf_files:
            print(f"   - {pdf.name}")
        
        # Test RAG initialization
        try:
            from api_final_agent.essence.agents.orchestrator import AgentOrchestrator
            
            print("\n🔄 Test d'initialisation du RAG engine...")
            orchestrator = AgentOrchestrator(data_dir=str(data_dir))
            success = orchestrator.initialize_research(force_reload=False)
            
            if success:
                print("✅ RAG engine initialisé avec succès!")
                
                # Test a simple query
                print("\n🔄 Test d'une requête RAG...")
                result = orchestrator.research_agent.execute({
                    'query': 'What are the key factors for consumer acceptance of plant-based products?',
                    'domain': 'Plant-Based',
                    'max_results': 3
                })
                
                if result.get('status') == 'success':
                    print("✅ Requête RAG réussie!")
                    data = result.get('data', {})
                    citations = data.get('citations', [])
                    print(f"   Citations trouvées: {len(citations)}")
                    for i, citation in enumerate(citations[:3], 1):
                        print(f"   {i}. {citation.get('source', 'Unknown')}")
                else:
                    print(f"❌ Requête RAG échouée: {result.get('message', 'Unknown error')}")
            else:
                print("❌ Échec de l'initialisation du RAG engine")
                
        except Exception as e:
            print(f"❌ Erreur lors du test RAG: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Répertoire data introuvable!")


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 TEST COMPLET API_FINAL_AGENT")
    print("="*80)
    
    # Check environment
    print("\n📋 Vérification de l'environnement:")
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"   OPENAI_API_KEY: {'✅ Configuré' if api_key else '❌ Manquant'}")
    
    tavily_key = os.getenv("TAVILY_API_KEY")
    print(f"   TAVILY_API_KEY: {'✅ Configuré' if tavily_key else '⚠️  Optionnel'}")
    
    if not api_key:
        print("\n❌ OPENAI_API_KEY est requis!")
        return
    
    # Run tests
    await test_pdf_access()
    await test_essence_pipeline()
    await test_ace_pipeline()
    await test_unified_output()
    
    print("\n" + "="*80)
    print("✅ TESTS TERMINÉS!")
    print("="*80)
    print("\n📁 Vérifiez les résultats dans: API_Final_Agent/artifacts/")


if __name__ == "__main__":
    asyncio.run(main())
