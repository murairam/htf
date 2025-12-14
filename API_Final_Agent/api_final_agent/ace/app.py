"""
Streamlit Web Interface for ACE Product Intelligence System.

Allows users to:
- Enter product barcode or search by name
- Upload packaging images
- Define business objectives
- View Generator analysis, Reflector insights, and Curator updates
- Explore the evolving playbook
"""
import streamlit as st
import json
from typing import Optional

from . import config as config_module
from .config import ACEConfig, LLMConfig, PlaybookConfig
from .playbook import PlaybookManager, deduplicate_playbook
from .agents import ACEPipeline
from .product_data import (
    OpenFoodFactsClient, 
    ImageAnalyzer, 
    NormalizedProductData,
    ImageAnalysisResult,
    create_sample_product_data,
    create_sample_image_analysis
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="ACE Product Intelligence",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# SESSION STATE
# =============================================================================

def init_session_state():
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = None
    if "product_data" not in st.session_state:
        st.session_state.product_data = None
    if "image_analysis" not in st.session_state:
        st.session_state.image_analysis = None
    if "current_result" not in st.session_state:
        st.session_state.current_result = None
    if "history" not in st.session_state:
        st.session_state.history = []
    if "api_key" not in st.session_state:
        st.session_state.api_key = None

init_session_state()


# =============================================================================
# SIDEBAR
# =============================================================================

def render_sidebar():
    st.sidebar.title(" Configuration")
    
    st.sidebar.subheader("LLM Settings")
    
    provider = st.sidebar.selectbox(
        "Provider",
        ["openai", "anthropic", "google", "mock"],
        index=0
    )
    
    model_options = {
        "openai": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o"],
        "anthropic": ["claude-3-opus-20240229", "claude-3-sonnet-20240229"],
        "google": ["gemini-pro", "gemini-1.5-pro"],
        "mock": ["mock-model"]
    }
    
    model = st.sidebar.selectbox(
        "Model",
        model_options.get(provider, ["gpt-4"])
    )
    
    api_key = st.sidebar.text_input("API Key", type="password")
    
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.0, 0.1)
    
    st.sidebar.divider()
    
    playbook_path = st.sidebar.text_input("Playbook Path", value="playbook.json")
    
    st.sidebar.divider()
    
    if st.sidebar.button(" Initialize Pipeline", type="primary", use_container_width=True):
        try:
            llm_config = LLMConfig(
                provider=provider,
                model=model,
                temperature=temperature,
                stream=True,
                api_key=api_key if api_key else None
            )
            
            playbook_config = PlaybookConfig(path=playbook_path)
            ace_config = ACEConfig(llm=llm_config, playbook=playbook_config)
            
            st.session_state.pipeline = ACEPipeline(ace_config)
            st.session_state.api_key = api_key if api_key else None
            st.sidebar.success(" Pipeline initialized!")
        except Exception as e:
            st.sidebar.error(f" Error: {e}")
    
    if st.session_state.pipeline:
        st.sidebar.success("Pipeline: Active")
        stats = st.session_state.pipeline.get_playbook_stats()
        st.sidebar.metric("Playbook Bullets", stats.get("total_bullets", 0))
    else:
        st.sidebar.warning("Pipeline: Not initialized")


# =============================================================================
# MAIN CONTENT
# =============================================================================

def render_header():
    st.title(" ACE Product Intelligence")
    st.markdown("""
    **Agentic Context Engineering** for product analysis and marketing intelligence.
    
    Enter a product barcode, define your business objective, and get AI-powered analysis
    that improves over time through learned insights.
    """)


def render_product_input():
    st.subheader(" Product Input")
    
    tab1, tab2, tab3 = st.tabs(["Barcode Lookup", "Manual Entry", "Sample Data"])
    
    with tab1:
        barcode = st.text_input("Enter Barcode", placeholder="e.g., 3017620422003")
        
        if st.button(" Fetch Product"):
            if barcode:
                with st.spinner("Fetching from OpenFoodFacts..."):
                    client = OpenFoodFactsClient()
                    product = client.get_product_by_barcode(barcode)
                    
                    if product:
                        st.session_state.product_data = product
                        st.success(f"Found: {product.name}")
                        
                        # Create image analysis with API key if available
                        api_key = st.session_state.get('api_key')
                        analyzer = ImageAnalyzer(api_key=api_key, model="gpt-4o")
                        st.session_state.image_analysis = analyzer.analyze_from_url(
                            product.image_front_url
                        )
                    else:
                        st.error("Product not found")
    
    with tab2:
        st.markdown("Enter product details manually:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Product Name")
            brand = st.text_input("Brand")
            category = st.text_input("Category")
        
        with col2:
            ingredients = st.text_area("Ingredients", height=100)
            packaging = st.text_input("Packaging Type")
        
        if st.button(" Save Manual Entry"):
            st.session_state.product_data = NormalizedProductData(
                name=name,
                brand=brand,
                plant_based_category=category,
                ingredients_text=ingredients
            )
            st.session_state.image_analysis = ImageAnalysisResult.empty()
            st.success("Product data saved!")
    
    with tab3:
        st.markdown("Use sample data for testing:")
        if st.button(" Load Sample (Nutella)"):
            st.session_state.product_data = create_sample_product_data()
            st.session_state.image_analysis = create_sample_image_analysis()
            st.success("Sample data loaded!")
    
    # Show current product
    if st.session_state.product_data:
        st.divider()
        st.markdown("### Current Product")
        
        product = st.session_state.product_data
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Product", product.name or "Unknown")
        col2.metric("Brand", product.brand or "Unknown")
        col3.metric("Nutriscore", product.nutriscore.upper() if product.nutriscore else "N/A")
        
        with st.expander("Full Product Data"):
            st.json(product.to_dict())


def render_image_analysis():
    st.subheader(" Image Analysis")
    
    if st.session_state.image_analysis:
        analysis = st.session_state.image_analysis
        
        if analysis.image_description:
            st.markdown("### 📸 ***Package Description***")
            st.markdown(analysis.image_description)
        
        # Display observations if available
        if hasattr(analysis, 'observations') and analysis.observations:
            st.markdown("### 👁️ ***Observations***")
            for obs in analysis.observations:
                st.markdown(f"- {obs}")
        
        # Display detected problems if available
        if hasattr(analysis, 'problemes_detectes') and analysis.problemes_detectes:
            st.markdown("### ⚠️ ***Problèmes Détectés***")
            for prob in analysis.problemes_detectes:
                if isinstance(prob, dict):
                    gravite_icon = {"Critique": "🔴", "Important": "🟠", "Mineur": "🟡"}.get(prob.get("gravite", ""), "⚪")
                    st.markdown(f"""
                    {gravite_icon} **{prob.get('probleme', 'N/A')}**
                    - *Indice visuel:* {prob.get('indice_visuel', 'N/A')}
                    - *Gravité:* {prob.get('gravite', 'N/A')}
                    - *Impact:* {prob.get('impact', 'N/A')}
                    """)
                else:
                    st.markdown(f"- {prob}")
    
    # Manual image analysis input
    with st.expander(" Add Manual Image Analysis"):
        description = st.text_area(
            "Package Description",
            height=100,
            placeholder="Describe the current packaging appearance, colors, design elements, etc."
        )
        
        if st.button(" Save Image Analysis"):
            st.session_state.image_analysis = ImageAnalysisResult(
                image_description=description,
                observations=[],
                problemes_detectes=[],
                attractiveness_improvements=[]
            )
            st.success("Image analysis saved!")


def render_objective_input():
    st.subheader(" Business Objective")
    
    # Structured objectives that match the scoring weights
    objective_options = {
        "": "Select an objective...",
        "reduce_upf_perception": " Reduce Ultra-Processed Perception (Focus: Utility 40%, Positioning 40%)",
        "launch_in_gms": " Launch in GMS/Retail (Focus: Attractiveness 40%)",
        "reposition_brand": " Reposition Brand (Focus: Positioning 40%)",
        "increase_flexitarian_appeal": " Increase Flexitarian Appeal (Focus: Attractiveness 45%)"
    }
    
    selected = st.selectbox(
        "Select Business Objective:",
        options=list(objective_options.keys()),
        format_func=lambda x: objective_options[x]
    )
    
    # Show weight breakdown
    if selected:
        weights = {
            "reduce_upf_perception": {"Attractiveness": "20%", "Utility": "40%", "Positioning": "40%"},
            "launch_in_gms": {"Attractiveness": "40%", "Utility": "30%", "Positioning": "30%"},
            "reposition_brand": {"Attractiveness": "30%", "Utility": "30%", "Positioning": "40%"},
            "increase_flexitarian_appeal": {"Attractiveness": "45%", "Utility": "35%", "Positioning": "20%"}
        }
        if selected in weights:
            cols = st.columns(3)
            for i, (metric, weight) in enumerate(weights[selected].items()):
                cols[i].caption(f"**{metric}:** {weight}")
    
    # Optional additional context
    additional_context = st.text_area(
        "Additional Context (optional)",
        height=80,
        placeholder="Add specific requirements or context for the analysis..."
    )
    
    objective = selected
    if additional_context:
        objective = f"{selected} | Context: {additional_context}"
    
    return objective


def render_analysis_controls(objective: str):
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        run_full = st.button(" Run Full Analysis", type="primary", use_container_width=True)
    
    with col2:
        generate_only = st.button(" Quick Analysis", use_container_width=True)
    
    with st.expander(" Training Options"):
        feedback = st.text_area(
            "Feedback for Reflector",
            height=80,
            help="Optional feedback to improve learning"
        )
    
    return run_full, generate_only, feedback


def run_analysis(objective: str, full_pipeline: bool, feedback: str = None):
    if not st.session_state.pipeline:
        st.error("Please initialize the pipeline first!")
        return
    
    if not st.session_state.product_data:
        st.error("Please load product data first!")
        return
    
    if not objective.strip():
        st.error("Please enter a business objective!")
        return
    
    product_data = st.session_state.product_data.to_dict()
    image_analysis = st.session_state.image_analysis.to_dict() if st.session_state.image_analysis else {}
    
    with st.spinner("Analyzing product..."):
        try:
            if full_pipeline:
                result = st.session_state.pipeline.run(
                    product_data=product_data,
                    image_analysis=image_analysis,
                    business_objective=objective,
                    feedback=feedback
                )
                
                result_dict = result.to_dict()
                st.session_state.current_result = result_dict
                
                # Safely get the global score
                try:
                    gen_output = result_dict.get("generator_output", {})
                    scores = gen_output.get("scores", {})
                    global_score = scores.get("global_score", 0)
                    
                    st.session_state.history.append({
                        "product": st.session_state.product_data.name,
                        "objective": objective[:50],
                        "global_score": global_score
                    })
                except Exception as score_error:
                    st.warning(f"Could not extract score: {score_error}")
            else:
                output = st.session_state.pipeline.generate_only(
                    product_data=product_data,
                    image_analysis=image_analysis,
                    business_objective=objective
                )
                
                st.session_state.current_result = {
                    "generator_output": output.to_dict(),
                    "reflector_output": None,
                    "curator_output": None
                }
            
            st.success(" Analysis complete!")
            
        except Exception as e:
            st.error(f" Error during analysis: {str(e)}")
            import traceback
            error_details = traceback.format_exc()
            st.code(error_details)
            st.error("Please check your API key and model configuration.")


def render_results():
    if not st.session_state.current_result:
        st.info("Run an analysis to see results here.")
        return
    
    result = st.session_state.current_result
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        " Scores & Analysis",
        " Reflector",
        " Curator",
        " Playbook",
        "📤 Export"
    ])
    
    with tab1:
        render_generator_output(result.get("generator_output"))
    
    with tab2:
        render_reflector_output(result.get("reflector_output"))
    
    with tab3:
        render_curator_output(result.get("curator_output"), result.get("added_bullets", []))
    
    with tab4:
        render_playbook_view()
    
    with tab5:
        render_export_button()


def render_generator_output(output: Optional[dict]):
    if not output:
        st.warning("No generator output available.")
        return
    
    st.subheader("Product Intelligence Scores")
    
    # Display objective and confidence
    objective = output.get("objective", "N/A")
    confidence = output.get("confidence", "N/A")
    
    col_obj, col_conf = st.columns(2)
    col_obj.info(f" **Objective:** {objective}")
    confidence_color = {"high": "", "medium": "", "low": ""}.get(confidence, "")
    col_conf.info(f"{confidence_color} **Confidence:** {confidence}")
    
    st.divider()
    
    # Main scores (0-100 scale now)
    scores = output.get("scores", {})
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(" Attractiveness", f"{scores.get('attractiveness_score', 0):.1f}/100")
    col2.metric(" Utility", f"{scores.get('utility_score', 0):.1f}/100")
    col3.metric(" Positioning", f"{scores.get('positioning_score', 0):.1f}/100")
    col4.metric(" Global Score", f"{scores.get('global_score', 0):.1f}/100")
    
    st.divider()
    
    # Criteria details
    criteria = output.get("criteria", {})
    if criteria:
        with st.expander(" Detailed Criteria Breakdown"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("** Attractiveness Criteria**")
                attr_criteria = criteria.get("attractiveness", {})
                for key, value in attr_criteria.items():
                    emoji = "" if value in ["yes", "simple", "clear", "familiar"] else "" if "partial" in str(value).lower() or "somewhat" in str(value).lower() or "moderate" in str(value).lower() or "weak" in str(value).lower() else ""
                    st.markdown(f"{emoji} **{key}:** {value}")
            
            with col2:
                st.markdown("** Utility Criteria**")
                util_criteria = criteria.get("utility", {})
                for key, value in util_criteria.items():
                    emoji = "" if value in ["clear", "coherent", "focused"] else "" if "partial" in str(value).lower() or "somewhat" in str(value).lower() else ""
                    st.markdown(f"{emoji} **{key}:** {value}")
            
            with col3:
                st.markdown("** Positioning Criteria**")
                pos_criteria = criteria.get("positioning", {})
                for key, value in pos_criteria.items():
                    emoji = "" if value in ["clear", "consistent", "low"] else "" if "partial" in str(value).lower() or "somewhat" in str(value).lower() or "moderate" in str(value).lower() else ""
                    st.markdown(f"{emoji} **{key}:** {value}")
    
    st.divider()
    
    # Explanations
    explanations = output.get("explanations", {})
    if explanations:
        with st.expander(" Evidence-Based Explanations"):
            for category, expl_list in explanations.items():
                if expl_list:
                    st.markdown(f"**{category.title()}:**")
                    for expl in expl_list:
                        st.markdown(f"- {expl}")
    
    st.divider()
    
    # Analysis (strengths, weaknesses, risks)
    analysis = output.get("analysis", {})
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("###  Strengths")
        for s in analysis.get("strengths", []):
            st.markdown(f"- {s}")
    
    with col2:
        st.markdown("###  Weaknesses")
        for w in analysis.get("weaknesses", []):
            st.markdown(f"- {w}")
    
    with col3:
        st.markdown("###  Risks")
        for r in analysis.get("risks", []):
            st.markdown(f"- {r}")
    
    st.divider()
    
    # Packaging Improvement Proposals
    st.markdown("###  Packaging Improvement Proposals")
    packaging_proposals = output.get("packaging_improvement_proposals", [])
    if packaging_proposals:
        for proposal in packaging_proposals:
            st.info(proposal)
    else:
        st.caption("No packaging proposals available")
    
    # Go-to-Market Recommendations
    st.markdown("###  Go-to-Market Recommendations")
    gtm = output.get("go_to_market_recommendations", {})
    if gtm:
        if gtm.get("shelf_positioning"):
            st.markdown("** Shelf Positioning:**")
            st.write(gtm.get("shelf_positioning"))
        if gtm.get("b2b_targeting"):
            st.markdown("** B2B Targeting:**")
            st.write(gtm.get("b2b_targeting"))
        if gtm.get("regional_relevance"):
            st.markdown("** Regional Relevance:**")
            st.write(gtm.get("regional_relevance"))
    else:
        st.caption("No GTM recommendations available")
    
    # Internal Reasoning (expandable)
    with st.expander(" Internal Reasoning"):
        reasoning = output.get("internal_reasoning", "")
        if reasoning:
            st.markdown(reasoning)
        else:
            st.caption("No reasoning details available")
            # Debug: show what keys are actually in output
            with st.expander(" Debug: Available keys in output"):
                st.json(list(output.keys()))
                if "internal_reasoning" in output:
                    st.write(f"internal_reasoning value: {repr(output['internal_reasoning'])}")
    
    if output.get("used_bullet_ids"):
        st.markdown("**Playbook bullets used:** " + ", ".join(output.get("used_bullet_ids", [])))


def render_export_button():
    """Render the export button to download complete product intelligence as JSON."""
    if not st.session_state.current_result:
        st.info("Run an analysis first to export results.")
        return
    
    st.markdown("## 📤 Export Complete Product Intelligence")
    st.markdown("---")
    
    st.markdown("""
    Export ***ALL knowledge*** for this product in a comprehensive JSON format:
    
    | Category | Contents |
    |----------|----------|
    | 📦 **Product Data** | Name, brand, ingredients, NOVA, nutrients, labels, packaging |
    | 🖼️ **Image Analysis** | Package description, observations, detected problems |
    | 📊 **Scores & Criteria** | Attractiveness, Utility, Positioning, Global Score |
    | 📝 **Explanations** | Evidence-based justifications for each score |
    | 💪 **SWOT Analysis** | Strengths, Weaknesses, Risks |
    | 📦 **Packaging Proposals** | Improvement recommendations |
    | 🚀 **Go-to-Market Strategy** | Shelf positioning, B2B targeting, regional relevance |
    | 🎯 **Business Objective Response** | How the product responds to the stated objective |
    """)
    
    # Build comprehensive export data
    import datetime
    
    generator_output = st.session_state.current_result.get("generator_output", {})
    reflector_output = st.session_state.current_result.get("reflector_output", {})
    
    # Get product and image data
    product_data = st.session_state.product_data.to_dict() if st.session_state.product_data else {}
    image_data = st.session_state.image_analysis.to_dict() if st.session_state.image_analysis else {}
    
    # Build complete export
    export_data = {
        "export_metadata": {
            "export_date": datetime.datetime.now().isoformat(),
            "export_type": "ACE Plant-Based Product Intelligence - Complete Report",
            "version": "1.0.0"
        },
        
        "business_objective": {
            "objective_key": generator_output.get("objective", ""),
            "objective_description": {
                "reduce_upf_perception": "Reduce Ultra-Processed Perception - Focus on clean label and natural positioning",
                "launch_in_gms": "Launch in GMS/Retail - Focus on shelf appeal and mass market positioning",
                "reposition_brand": "Reposition Brand - Focus on brand coherence and market positioning",
                "increase_flexitarian_appeal": "Increase Flexitarian Appeal - Focus on attractiveness for plant-curious consumers"
            }.get(generator_output.get("objective", ""), "Custom objective"),
            "scoring_weights": {
                "reduce_upf_perception": {"attractiveness": 0.20, "utility": 0.40, "positioning": 0.40},
                "launch_in_gms": {"attractiveness": 0.40, "utility": 0.30, "positioning": 0.30},
                "reposition_brand": {"attractiveness": 0.30, "utility": 0.30, "positioning": 0.40},
                "increase_flexitarian_appeal": {"attractiveness": 0.45, "utility": 0.35, "positioning": 0.20}
            }.get(generator_output.get("objective", ""), {"attractiveness": 0.33, "utility": 0.34, "positioning": 0.33})
        },
        
        "product_information": {
            "basic_info": {
                "name": product_data.get("name", ""),
                "brand": product_data.get("brand", ""),
                "product_id": product_data.get("product_id", ""),
                "category": product_data.get("plant_based_category", "")
            },
            "ingredients": {
                "ingredients_text": product_data.get("ingredients_text", ""),
                "ingredients_count": product_data.get("ingredients_count", 0),
                "additives_count": product_data.get("additives_count", 0)
            },
            "nutrition": {
                "nova_group": product_data.get("nova_group", 0),
                "nutriscore": product_data.get("nutriscore", ""),
                "nutriments": product_data.get("nutriments", {})
            },
            "labels_certifications": product_data.get("labels", []),
            "packaging": product_data.get("packaging", {}),
            "origin": product_data.get("origin", ""),
            "countries": product_data.get("countries", [])
        },
        
        "image_analysis": {
            "package_description": image_data.get("image_description", ""),
            "visual_observations": image_data.get("observations", []),
            "detected_problems": image_data.get("problemes_detectes", [])
        },
        
        "scoring_results": {
            "confidence_level": generator_output.get("confidence", ""),
            "scores": {
                "attractiveness_score": generator_output.get("scores", {}).get("attractiveness_score", 0),
                "utility_score": generator_output.get("scores", {}).get("utility_score", 0),
                "positioning_score": generator_output.get("scores", {}).get("positioning_score", 0),
                "global_score": generator_output.get("scores", {}).get("global_score", 0)
            },
            "criteria_breakdown": {
                "attractiveness": generator_output.get("criteria", {}).get("attractiveness", {}),
                "utility": generator_output.get("criteria", {}).get("utility", {}),
                "positioning": generator_output.get("criteria", {}).get("positioning", {})
            }
        },
        
        "evidence_based_explanations": generator_output.get("explanations", {}),
        
        "swot_analysis": {
            "strengths": generator_output.get("analysis", {}).get("strengths", []),
            "weaknesses": generator_output.get("analysis", {}).get("weaknesses", []),
            "risks": generator_output.get("analysis", {}).get("risks", [])
        },
        
        "packaging_improvement_proposals": generator_output.get("packaging_improvement_proposals", []),
        
        "go_to_market_strategy": {
            "shelf_positioning": generator_output.get("go_to_market_recommendations", {}).get("shelf_positioning", ""),
            "b2b_targeting": generator_output.get("go_to_market_recommendations", {}).get("b2b_targeting", ""),
            "regional_relevance": generator_output.get("go_to_market_recommendations", {}).get("regional_relevance", "")
        },
        
        "quality_insights": {
            "reflector_analysis": reflector_output.get("analysis", "") if reflector_output else "",
            "key_insights": reflector_output.get("key_insights", "") if reflector_output else "",
            "improvement_guidelines": reflector_output.get("improved_reasoning_guidelines", "") if reflector_output else ""
        }
    }
    
    # Generate filename based on product name
    product_name = "product"
    if st.session_state.product_data and st.session_state.product_data.name:
        product_name = st.session_state.product_data.name.replace(" ", "_").replace("/", "_").replace("\\", "_")[:30]
    
    filename = f"ace_complete_intelligence_{product_name}.json"
    
    st.markdown("---")
    
    # Preview section
    with st.expander("👁️ Preview Complete Export Data"):
        st.json(export_data)
    
    st.markdown("---")
    
    # Main export button - prominent
    st.download_button(
        label="📥 ***EXPORT COMPLETE PRODUCT INTELLIGENCE (JSON)***",
        data=json.dumps(export_data, indent=2, ensure_ascii=False, default=str),
        file_name=filename,
        mime="application/json",
        type="primary",
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Additional export options
    st.markdown("### Additional Export Options")
    col1, col2 = st.columns(2)
    
    with col1:
        # Export only scores summary
        scores_only = {
            "product_name": product_data.get("name", "Unknown"),
            "objective": generator_output.get("objective", ""),
            "scores": generator_output.get("scores", {}),
            "confidence": generator_output.get("confidence", ""),
            "criteria": generator_output.get("criteria", {})
        }
        st.download_button(
            label="📊 Scores & Criteria Only",
            data=json.dumps(scores_only, indent=2, ensure_ascii=False, default=str),
            file_name=f"scores_{product_name}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Export market strategy only
        market_strategy = {
            "product_name": product_data.get("name", "Unknown"),
            "objective": generator_output.get("objective", ""),
            "go_to_market_strategy": export_data["go_to_market_strategy"],
            "packaging_proposals": generator_output.get("packaging_improvement_proposals", []),
            "swot": export_data["swot_analysis"]
        }
        st.download_button(
            label="🚀 Market Strategy Only",
            data=json.dumps(market_strategy, indent=2, ensure_ascii=False, default=str),
            file_name=f"market_strategy_{product_name}.json",
            mime="application/json",
            use_container_width=True
        )
    
    st.markdown("---")
    st.success("✅ All product intelligence is ready for export!")


def render_reflector_output(output: Optional[dict]):
    if not output:
        st.info("Run full analysis to see Reflector output.")
        return
    
    st.subheader(" Reflector Analysis")
    
    st.markdown("###  Key Insights")
    key_insights = output.get("key_insights", "")
    if key_insights:
        st.success(key_insights)
    else:
        st.info("No key insights generated")
    
    with st.expander(" Quality Analysis"):
        analysis = output.get("analysis", "")
        if analysis:
            st.markdown(analysis)
        else:
            st.caption("No detailed analysis available")
    
    with st.expander(" Identified Errors"):
        errors = output.get("identified_errors", "")
        if errors:
            st.markdown(errors)
        else:
            st.caption("No errors identified")
    
    with st.expander(" Root Causes"):
        causes = output.get("root_causes", "")
        if causes:
            st.markdown(causes)
        else:
            st.caption("N/A")
    
    with st.expander(" Improved Guidelines"):
        guidelines = output.get("improved_reasoning_guidelines", "")
        if guidelines:
            st.markdown(guidelines)
        else:
            st.caption("No guidelines provided")
    
    bullet_eval = output.get("bullet_evaluation", [])
    if bullet_eval:
        st.markdown("###  Bullet Evaluation")
        for be in bullet_eval:
            tag_icon = {"helpful": "", "misused": "", "irrelevant": ""}.get(be.get("tag"), "")
            st.markdown(f"{tag_icon} `{be.get('id')}`: {be.get('tag')}")
    else:
        st.caption("No bullet evaluation available")


def render_curator_output(output: Optional[dict], added_bullets: list):
    if not output:
        st.info("Run full analysis to see Curator output.")
        return
    
    st.subheader("Curator Updates")
    
    with st.expander(" Curator's Reasoning"):
        st.markdown(output.get("reasoning", ""))
    
    operations = output.get("operations", [])
    
    if operations:
        st.markdown("###  Planned Operations")
        for i, op in enumerate(operations, 1):
            with st.expander(f"Op {i}: {op.get('type')}  {op.get('section')}"):
                st.markdown(f"**Section:** {op.get('section')}")
                st.markdown(f"**Content:** {op.get('content')}")
    else:
        st.info("No new knowledge needed.")
    
    if added_bullets:
        st.markdown("###  Added to Playbook")
        for b in added_bullets:
            st.success(f"**{b.get('id')}**: {b.get('content')[:100]}...")


def render_playbook_view():
    if not st.session_state.pipeline:
        st.warning("Initialize pipeline to view playbook.")
        return
    
    playbook = st.session_state.pipeline.get_playbook()
    stats = playbook.get_stats()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total", stats.get("total_bullets", 0))
    col2.metric("Scoring Rules", stats.get("sections", {}).get("scoring_rules", 0))
    col3.metric("Heuristics", stats.get("sections", {}).get("heuristics", 0))
    col4.metric("Pitfalls", stats.get("sections", {}).get("pitfalls", 0))
    col5.metric("Patterns", stats.get("sections", {}).get("marketing_patterns", 0) + 
                stats.get("sections", {}).get("packaging_patterns", 0))
    
    sections = ["scoring_rules", "heuristics", "pitfalls", "marketing_patterns", "packaging_patterns"]
    
    for section in sections:
        bullets = playbook.get_section(section)
        if bullets:
            with st.expander(f" {section.upper().replace('_', ' ')} ({len(bullets)})"):
                for b in bullets:
                    eff = b.effectiveness_score
                    icon = "" if eff > 0.5 else "" if eff >= 0 else ""
                    st.markdown(f"**{b.id}** {icon}\n\n{b.content}\n\n*helpful={b.helpful_count} misused={b.misused_count}*")
                    st.divider()
    
    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(" Deduplicate"):
            removed = deduplicate_playbook(playbook)
            if removed:
                st.session_state.pipeline.playbook_manager.save()
                st.success(f"Removed {len(removed)} duplicates")
            else:
                st.info("No duplicates found")
    
    with col2:
        if st.button(" Export"):
            st.download_button(
                "Download JSON",
                json.dumps(playbook.to_dict(), indent=2),
                file_name="playbook_export.json",
                mime="application/json"
            )


# =============================================================================
# MAIN
# =============================================================================

def main():
    render_sidebar()
    render_header()
    
    st.divider()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_product_input()
        
        st.divider()
        render_image_analysis()
        
        st.divider()
        objective = render_objective_input()
        
        run_full, generate_only, feedback = render_analysis_controls(objective)
        
        if run_full:
            run_analysis(objective, True, feedback)
        elif generate_only:
            run_analysis(objective, False)
        
        st.divider()
        render_results()
    
    with col2:
        st.subheader(" History")
        if st.session_state.history:
            for i, h in enumerate(reversed(st.session_state.history[-10:]), 1):
                st.markdown(f"**{i}.** {h['product']}")
                st.caption(f"Score: {h['global_score']:.1f} | {h['objective']}")
        else:
            st.info("No analysis history yet")


if __name__ == "__main__":
    main()
