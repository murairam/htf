"""
Competitor Data for Plant-Based Products
Static data for competitor intelligence analysis
"""

# Competitor data for plant-based burgers
PLANT_BASED_COMPETITORS = [
    {
        "company": "Beyond Meat",
        "product": "Beyond Burger",
        "price_per_kg": 30.0,
        "co2_emission_kg": 2.5,
        "marketing_claim": "Plant-based burger that looks and tastes like beef."
    },
    {
        "company": "Impossible Foods",
        "product": "Impossible Burger",
        "price_per_kg": 28.0,
        "co2_emission_kg": 2.2,
        "marketing_claim": "Made from plants, tastes like beef."
    },
    {
        "company": "Quorn",
        "product": "Quorn Meatless Burger",
        "price_per_kg": 20.0,
        "co2_emission_kg": 1.8,
        "marketing_claim": "High in protein, low in saturated fat."
    },
    {
        "company": "Garden Gourmet",
        "product": "Sensational Burger",
        "price_per_kg": 22.5,
        "co2_emission_kg": 2.0,
        "marketing_claim": "100% plant-based and delicious."
    },
    {
        "company": "Oumph!",
        "product": "Oumph! Burger",
        "price_per_kg": 24.0,
        "co2_emission_kg": 2.1,
        "marketing_claim": "Plant-based burger with a meaty texture."
    },
    {
        "company": "Lightlife",
        "product": "Lightlife Burger",
        "price_per_kg": 26.0,
        "co2_emission_kg": 2.4,
        "marketing_claim": "A delicious plant-based burger."
    },
    {
        "company": "Field Roast",
        "product": "Field Roast Burger",
        "price_per_kg": 27.0,
        "co2_emission_kg": 2.3,
        "marketing_claim": "Crafted with grains and vegetables."
    },
    {
        "company": "Dr. Praeger's",
        "product": "Dr. Praeger's California Burger",
        "price_per_kg": 23.0,
        "co2_emission_kg": 1.9,
        "marketing_claim": "Made with wholesome ingredients."
    },
    {
        "company": "Nuggs",
        "product": "Nuggs Plant-Based Burger",
        "price_per_kg": 29.0,
        "co2_emission_kg": 2.6,
        "marketing_claim": "The future of plant-based burgers."
    },
    {
        "company": "Alpha Foods",
        "product": "Alpha Burger",
        "price_per_kg": 25.0,
        "co2_emission_kg": 2.2,
        "marketing_claim": "Plant-based burger that satisfies."
    }
]


def get_competitor_data(product_category="plant-based-burger"):
    """
    Get competitor data for a specific product category.
    
    Args:
        product_category: Category of product (default: plant-based-burger)
        
    Returns:
        List of competitor dictionaries
    """
    # For now, we only have burger data
    # Can be extended with other categories
    if "burger" in product_category.lower() or "meat" in product_category.lower():
        return PLANT_BASED_COMPETITORS
    
    # Default to burger data
    return PLANT_BASED_COMPETITORS


def calculate_metrics(competitors):
    """
    Calculate aggregate metrics from competitor data.
    
    Args:
        competitors: List of competitor dictionaries
        
    Returns:
        Dictionary with metrics
    """
    if not competitors:
        return {}
    
    prices = [c["price_per_kg"] for c in competitors]
    co2_emissions = [c["co2_emission_kg"] for c in competitors]
    
    return {
        "avg_price_per_kg": sum(prices) / len(prices),
        "avg_co2_emission": sum(co2_emissions) / len(co2_emissions),
        "competitor_count": len(competitors),
        "price_range": {
            "min": min(prices),
            "max": max(prices)
        },
        "co2_range": {
            "min": min(co2_emissions),
            "max": max(co2_emissions)
        }
    }


def generate_visualizations(competitors):
    """
    Generate Plotly visualization data for competitors.
    
    Args:
        competitors: List of competitor dictionaries
        
    Returns:
        Dictionary with visualization data
    """
    companies = [c["company"] for c in competitors]
    prices = [c["price_per_kg"] for c in competitors]
    co2_emissions = [c["co2_emission_kg"] for c in competitors]
    
    # Price comparison chart
    price_chart = {
        "data": [{
            "x": companies,
            "y": prices,
            "type": "bar",
            "name": "Price per kg",
            "marker": {
                "color": prices,
                "colorscale": "Viridis",
                "showscale": True,
                "colorbar": {"title": "€/kg"}
            }
        }],
        "layout": {
            "title": "Price Comparison (€/kg)",
            "xaxis": {"title": "Company", "tickangle": -45},
            "yaxis": {"title": "Price (€/kg)"},
            "height": 400,
            "margin": {"b": 120}
        }
    }
    
    # CO2 emissions chart
    co2_chart = {
        "data": [{
            "x": companies,
            "y": co2_emissions,
            "type": "bar",
            "name": "CO2 Emissions",
            "marker": {
                "color": co2_emissions,
                "colorscale": "RdYlGn_r",
                "showscale": True,
                "colorbar": {"title": "kg CO2"}
            }
        }],
        "layout": {
            "title": "CO₂ Emissions (kg/kg product)",
            "xaxis": {"title": "Company", "tickangle": -45},
            "yaxis": {"title": "CO₂ Emission (kg)"},
            "height": 400,
            "margin": {"b": 120}
        }
    }
    
    # Scatter plot: Price vs Environmental Impact
    scatter_chart = {
        "data": [{
            "x": co2_emissions,
            "y": prices,
            "mode": "markers+text",
            "type": "scatter",
            "text": companies,
            "textposition": "top center",
            "marker": {
                "size": 15,
                "color": list(range(len(companies))),
                "colorscale": "Rainbow",
                "showscale": False,
                "line": {"width": 2, "color": "white"}
            },
            "hovertemplate": (
                "<b>%{text}</b><br>"
                "CO₂: %{x} kg<br>"
                "Price: €%{y}/kg<br>"
                "<extra></extra>"
            )
        }],
        "layout": {
            "title": "Price vs Environmental Impact",
            "xaxis": {"title": "CO₂ Emissions (kg)"},
            "yaxis": {"title": "Price (€/kg)"},
            "height": 500,
            "hovermode": "closest"
        }
    }
    
    return {
        "price_chart": price_chart,
        "co2_chart": co2_chart,
        "scatter_chart": scatter_chart
    }


def get_competitor_intelligence(product_category="plant-based-burger"):
    """
    Get complete competitor intelligence data.
    
    Args:
        product_category: Category of product
        
    Returns:
        Dictionary with competitors, metrics, and visualizations
    """
    competitors = get_competitor_data(product_category)
    metrics = calculate_metrics(competitors)
    visualizations = generate_visualizations(competitors)
    
    return {
        "competitors": competitors,
        "metrics": metrics,
        "visualizations": visualizations,
        "analysis_summary": f"Analysis of {len(competitors)} competitors in the {product_category} market. "
                          f"Average price: €{metrics['avg_price_per_kg']:.2f}/kg, "
                          f"Average CO₂: {metrics['avg_co2_emission']:.2f} kg/kg product.",
        "market_overview": "The plant-based burger market is highly competitive with established players "
                         "like Beyond Meat and Impossible Foods leading in brand recognition, while "
                         "newer entrants like Quorn and Garden Gourmet compete on price and sustainability."
    }
