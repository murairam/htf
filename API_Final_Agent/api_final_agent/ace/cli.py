"""
CLI for ACE Plant-Based Packaging Intelligence.
"""
import argparse
import json
import sys

from . import config as config_module
from .config import ACEConfig, LLMConfig
from .agents import ACEPipeline
from .product_data import OpenFoodFactsClient, ImageAnalyzer, create_sample_product_data, create_sample_image_analysis


def create_parser():
    parser = argparse.ArgumentParser(description="Plant-Based Packaging Intelligence CLI")
    parser.add_argument("--provider", "-p", default="openai", choices=["openai", "anthropic", "google", "mock"])
    parser.add_argument("--model", "-m", default="gpt-4o")
    parser.add_argument("--api-key", "-k", default=None)
    
    subparsers = parser.add_subparsers(dest="command")
    
    analyze = subparsers.add_parser("analyze", help="Analyze a product")
    analyze.add_argument("--barcode", help="Product barcode")
    analyze.add_argument("--objective", "-o", required=True, help="Business objective")
    analyze.add_argument("--sample", action="store_true", help="Use sample data")
    
    lookup = subparsers.add_parser("lookup", help="Lookup product")
    lookup.add_argument("barcode")
    
    return parser


def cmd_analyze(args):
    config = ACEConfig(llm=LLMConfig(provider=args.provider, model=args.model, api_key=args.api_key))
    pipeline = ACEPipeline(config)
    image_analyzer = ImageAnalyzer(api_key=args.api_key)
    
    if args.sample:
        product = create_sample_product_data()
        image_analysis = create_sample_image_analysis()
    elif args.barcode:
        client = OpenFoodFactsClient()
        product = client.get_product_by_barcode(args.barcode)
        if not product:
            print(f"Product not found: {args.barcode}")
            sys.exit(1)
        image_analysis = image_analyzer.analyze_from_url(product.image_front_url) if product.image_front_url else None
    else:
        print("Provide --barcode or --sample")
        sys.exit(1)
    
    print(f"\n🌱 Analyzing: {product.name}")
    print(f"Category: {product.plant_based_category}")
    print(f"Objective: {args.objective}\n")
    
    result = pipeline.analyze(
        product_data=product.to_dict(),
        image_analysis=image_analysis.to_dict() if image_analysis else {},
        business_objective=args.objective
    )
    
    scores = result.get("scores", {})
    print("📊 SCORES")
    print(f"  Attractiveness:   {scores.get('attractiveness', 0):.1f}/10")
    print(f"  Utility:          {scores.get('utility', 0):.1f}/10")
    print(f"  Price Coherence:  {scores.get('price_coherence', 0):.1f}/10")
    print(f"  Global Score:     {scores.get('global_score', 0):.1f}/10")
    
    analysis = result.get("analysis", {})
    print("\n✅ STRENGTHS")
    for s in analysis.get("strengths", []):
        print(f"  • {s}")
    print("\n⚠️ WEAKNESSES")
    for w in analysis.get("weaknesses", []):
        print(f"  • {w}")
    print("\n🚨 RISKS")
    for r in analysis.get("risks", []):
        print(f"  • {r}")
    
    print("\n📦 PACKAGING IMPROVEMENTS")
    for p in result.get("packaging_improvement_proposals", []):
        print(f"  • {p}")
    
    gtm = result.get("go_to_market_recommendations", {})
    print("\n🚀 GO-TO-MARKET")
    print(f"  Shelf: {gtm.get('shelf_positioning', 'N/A')}")
    print(f"  B2B: {gtm.get('b2b_targeting', 'N/A')}")
    print(f"  Regional: {gtm.get('regional_relevance', 'N/A')}")


def cmd_lookup(args):
    client = OpenFoodFactsClient()
    product = client.get_product_by_barcode(args.barcode)
    
    if product:
        print(f"\n🌱 {product.name}")
        print(f"Brand: {product.brand}")
        print(f"Category: {product.plant_based_category}")
        print(f"NOVA: {product.nova_group}, Nutriscore: {product.nutriscore}")
        print(f"Ingredients: {product.ingredients_count}, Additives: {product.additives_count}")
        print(f"Labels: {', '.join(product.labels)}")
    else:
        print(f"Product not found: {args.barcode}")


def main():
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    if args.command == "analyze":
        cmd_analyze(args)
    elif args.command == "lookup":
        cmd_lookup(args)


if __name__ == "__main__":
    main()