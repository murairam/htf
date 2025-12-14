"""
Visualizations Generator
Creates Plotly charts from analysis data for frontend display.
"""

from typing import Dict, Any, List, Optional
import json


def generate_competitor_price_chart(competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate bar chart for competitor price comparison.
    
    Args:
        competitors: List of competitor data with price_per_kg
        
    Returns:
        Plotly chart configuration as dict
    """
    if not competitors:
        return {}
    
    companies = [c.get('company', 'Unknown') for c in competitors]
    prices = [c.get('price_per_kg', 0) for c in competitors]
    
    chart = {
        "data": [
            {
                "type": "bar",
                "x": companies,
                "y": prices,
                "marker": {
                    "color": prices,
                    "colorscale": "Viridis",
                    "showscale": True,
                    "colorbar": {
                        "title": "€/kg"
                    }
                },
                "text": [f"€{p:.2f}/kg" for p in prices],
                "textposition": "outside",
                "hovertemplate": "<b>%{x}</b><br>Price: €%{y:.2f}/kg<extra></extra>"
            }
        ],
        "layout": {
            "title": {
                "text": "Price Comparison (€/kg)",
                "font": {"size": 18, "family": "Arial, sans-serif"}
            },
            "xaxis": {
                "title": "Company",
                "tickangle": -45
            },
            "yaxis": {
                "title": "Price (€/kg)"
            },
            "hovermode": "closest",
            "plot_bgcolor": "rgba(240, 240, 240, 0.5)",
            "paper_bgcolor": "white",
            "margin": {"l": 60, "r": 40, "t": 80, "b": 120}
        }
    }
    
    return chart


def generate_competitor_co2_chart(competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate bar chart for competitor CO2 emissions comparison.
    
    Args:
        competitors: List of competitor data with co2_emission_kg
        
    Returns:
        Plotly chart configuration as dict
    """
    if not competitors:
        return {}
    
    companies = [c.get('company', 'Unknown') for c in competitors]
    co2_values = [c.get('co2_emission_kg', 0) for c in competitors]
    
    chart = {
        "data": [
            {
                "type": "bar",
                "x": companies,
                "y": co2_values,
                "marker": {
                    "color": co2_values,
                    "colorscale": "RdYlGn",
                    "reversescale": True,
                    "showscale": True,
                    "colorbar": {
                        "title": "kg CO₂"
                    }
                },
                "text": [f"{co2:.2f} kg" for co2 in co2_values],
                "textposition": "outside",
                "hovertemplate": "<b>%{x}</b><br>CO₂: %{y:.2f} kg/kg product<extra></extra>"
            }
        ],
        "layout": {
            "title": {
                "text": "CO₂ Emissions (kg/kg product)",
                "font": {"size": 18, "family": "Arial, sans-serif"}
            },
            "xaxis": {
                "title": "Company",
                "tickangle": -45
            },
            "yaxis": {
                "title": "CO₂ Emissions (kg)"
            },
            "hovermode": "closest",
            "plot_bgcolor": "rgba(240, 240, 240, 0.5)",
            "paper_bgcolor": "white",
            "margin": {"l": 60, "r": 40, "t": 80, "b": 120}
        }
    }
    
    return chart


def generate_price_vs_co2_scatter(competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate scatter plot for price vs CO2 emissions.
    
    Args:
        competitors: List of competitor data with price_per_kg and co2_emission_kg
        
    Returns:
        Plotly chart configuration as dict
    """
    if not competitors:
        return {}
    
    companies = [c.get('company', 'Unknown') for c in competitors]
    prices = [c.get('price_per_kg', 0) for c in competitors]
    co2_values = [c.get('co2_emission_kg', 0) for c in competitors]
    products = [c.get('product', '') for c in competitors]
    
    chart = {
        "data": [
            {
                "type": "scatter",
                "mode": "markers+text",
                "x": co2_values,
                "y": prices,
                "text": companies,
                "textposition": "top center",
                "marker": {
                    "size": [p * 2 for p in prices],  # Size based on price
                    "color": prices,
                    "colorscale": "Viridis",
                    "showscale": True,
                    "colorbar": {
                        "title": "Price (€/kg)"
                    },
                    "line": {
                        "width": 1,
                        "color": "white"
                    }
                },
                "hovertemplate": (
                    "<b>%{text}</b><br>"
                    "Product: " + "<br>".join([p[:30] + "..." if len(p) > 30 else p for p in products]) + "<br>"
                    "Price: €%{y:.2f}/kg<br>"
                    "CO₂: %{x:.2f} kg<br>"
                    "<extra></extra>"
                ),
                "customdata": products
            }
        ],
        "layout": {
            "title": {
                "text": "Price vs Environmental Impact",
                "font": {"size": 18, "family": "Arial, sans-serif"}
            },
            "xaxis": {
                "title": "CO₂ Emissions (kg/kg product)",
                "gridcolor": "rgba(200, 200, 200, 0.5)"
            },
            "yaxis": {
                "title": "Price (€/kg)",
                "gridcolor": "rgba(200, 200, 200, 0.5)"
            },
            "hovermode": "closest",
            "plot_bgcolor": "rgba(240, 240, 240, 0.3)",
            "paper_bgcolor": "white",
            "margin": {"l": 60, "r": 40, "t": 80, "b": 60}
        }
    }
    
    return chart


def generate_scores_radar_chart(scores: Dict[str, float]) -> Dict[str, Any]:
    """
    Generate radar chart for performance scores.
    
    Args:
        scores: Dictionary with attractiveness, utility, positioning, global scores
        
    Returns:
        Plotly chart configuration as dict
    """
    if not scores:
        return {}
    
    categories = []
    values = []
    
    score_mapping = {
        'attractiveness': 'Attractiveness',
        'attractiveness_score': 'Attractiveness',
        'utility': 'Utility',
        'utility_score': 'Utility',
        'positioning': 'Positioning',
        'positioning_score': 'Positioning',
        'global': 'Global',
        'global_score': 'Global'
    }
    
    for key, label in score_mapping.items():
        if key in scores and scores[key] is not None:
            if label not in categories:  # Avoid duplicates
                categories.append(label)
                values.append(float(scores[key]))
    
    # Close the radar chart
    if categories:
        categories.append(categories[0])
        values.append(values[0])
    
    chart = {
        "data": [
            {
                "type": "scatterpolar",
                "r": values,
                "theta": categories,
                "fill": "toself",
                "fillcolor": "rgba(99, 110, 250, 0.3)",
                "line": {
                    "color": "rgb(99, 110, 250)",
                    "width": 2
                },
                "marker": {
                    "size": 8,
                    "color": "rgb(99, 110, 250)"
                },
                "hovertemplate": "<b>%{theta}</b><br>Score: %{r:.1f}/100<extra></extra>"
            }
        ],
        "layout": {
            "title": {
                "text": "Performance Scores Overview",
                "font": {"size": 18, "family": "Arial, sans-serif"}
            },
            "polar": {
                "radialaxis": {
                    "visible": True,
                    "range": [0, 100],
                    "ticksuffix": "",
                    "gridcolor": "rgba(200, 200, 200, 0.5)"
                },
                "angularaxis": {
                    "gridcolor": "rgba(200, 200, 200, 0.5)"
                }
            },
            "showlegend": False,
            "paper_bgcolor": "white",
            "margin": {"l": 80, "r": 80, "t": 80, "b": 80}
        }
    }
    
    return chart


def generate_competitor_visualizations(competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate all competitor-related visualizations.
    
    Args:
        competitors: List of competitor data
        
    Returns:
        Dictionary with all charts
    """
    return {
        "price_chart": generate_competitor_price_chart(competitors),
        "co2_chart": generate_competitor_co2_chart(competitors),
        "scatter_chart": generate_price_vs_co2_scatter(competitors)
    }


def generate_all_visualizations(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate all visualizations from unified analysis data.
    
    Args:
        data: Unified analysis data from API_Final_Agent
        
    Returns:
        List of visualization objects for frontend
    """
    visuals = []
    
    # Extract competitors data
    competitors = []
    if 'competitor_intelligence' in data:
        competitors = data['competitor_intelligence'].get('competitors', [])
    elif 'competitor_analysis' in data:
        comp_data = data['competitor_analysis']
        if isinstance(comp_data, dict):
            competitors = comp_data.get('competitors', [])
        elif isinstance(comp_data, list):
            competitors = comp_data
    
    # Generate competitor visualizations
    if competitors:
        comp_viz = generate_competitor_visualizations(competitors)
        
        if comp_viz.get('price_chart'):
            visuals.append({
                "title": "Price Comparison",
                "type": "plotly_chart",
                "format": "plotly_json",
                "data_or_url": comp_viz['price_chart'],
                "path": "competitor_intelligence.visualizations.price_chart"
            })
        
        if comp_viz.get('co2_chart'):
            visuals.append({
                "title": "CO₂ Emissions Comparison",
                "type": "plotly_chart",
                "format": "plotly_json",
                "data_or_url": comp_viz['co2_chart'],
                "path": "competitor_intelligence.visualizations.co2_chart"
            })
        
        if comp_viz.get('scatter_chart'):
            visuals.append({
                "title": "Price vs Environmental Impact",
                "type": "plotly_chart",
                "format": "plotly_json",
                "data_or_url": comp_viz['scatter_chart'],
                "path": "competitor_intelligence.visualizations.scatter_chart"
            })
    
    # Extract scores data
    scores = {}
    if 'scoring_results' in data:
        scores = data['scoring_results'].get('scores', {})
    elif 'scores' in data:
        scores = data['scores']
    
    # Generate scores radar chart
    if scores:
        radar_chart = generate_scores_radar_chart(scores)
        if radar_chart:
            visuals.append({
                "title": "Performance Scores Overview",
                "type": "plotly_chart",
                "format": "plotly_json",
                "data_or_url": radar_chart,
                "path": "scoring_results.visualizations.radar_chart"
            })
    
    return visuals


def calculate_competitor_metrics(competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate aggregate metrics from competitor data.
    
    Args:
        competitors: List of competitor data
        
    Returns:
        Dictionary with metrics
    """
    if not competitors:
        return {
            "avg_price_per_kg": 0,
            "avg_co2_emission": 0,
            "competitor_count": 0,
            "price_range": {"min": 0, "max": 0}
        }
    
    prices = [c.get('price_per_kg', 0) for c in competitors if c.get('price_per_kg')]
    co2_values = [c.get('co2_emission_kg', 0) for c in competitors if c.get('co2_emission_kg')]
    
    return {
        "avg_price_per_kg": sum(prices) / len(prices) if prices else 0,
        "avg_co2_emission": sum(co2_values) / len(co2_values) if co2_values else 0,
        "competitor_count": len(competitors),
        "price_range": {
            "min": min(prices) if prices else 0,
            "max": max(prices) if prices else 0
        }
    }
