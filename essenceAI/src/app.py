"""
essenceAI - B2B Market Intelligence Platform
Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from competitor_data import CompetitorIntelligence
from rag_engine import RAGEngine

# Page configuration
st.set_page_config(
    page_title="essenceAI - Sustainable Food Intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .citation-box {
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 600;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'rag_engine' not in st.session_state:
    st.session_state.rag_engine = None
if 'index_loaded' not in st.session_state:
    st.session_state.index_loaded = False

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/667eea/ffffff?text=essenceAI", use_container_width=True)

    st.markdown("### 🎯 Domain Selection")
    category = st.selectbox(
        "Select Innovation Domain",
        ["Precision Fermentation", "Plant-Based", "Algae"],
        help="Choose the sustainable food sector to analyze"
    )

    st.markdown("### 🧠 Target Consumer Segment")
    st.markdown("*Optional: Add psychological targeting*")

    use_segment = st.checkbox(
        "Enable segment-specific insights",
        value=False,
        help="Get tailored marketing strategy based on consumer psychology"
    )

    if use_segment:
        segment = st.selectbox(
            "Consumer Psychology Profile",
            ["Skeptic", "High Essentialist", "Non-Consumer"],
            help="Based on Food Essentialism research (Cheon et al., 2025)"
        )
    else:
        segment = None

    st.markdown("---")

    st.markdown("### ⚙️ Settings")

    # API Status
    import os
    from dotenv import load_dotenv
    load_dotenv()

    openai_key = os.getenv("OPENAI_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")

    st.markdown("**API Status:**")
    st.markdown(f"{'✅' if openai_key else '❌'} OpenAI API")
    st.markdown(f"{'✅' if tavily_key else '⚠️'} Tavily API (Optional)")

    if not openai_key:
        st.error("⚠️ OpenAI API key required! Add to .env file")

    st.markdown("---")

    # Initialize RAG Engine
    if st.button("🔄 Initialize Research Database", use_container_width=True):
        with st.spinner("Loading research papers..."):
            try:
                data_dir = Path(__file__).parent.parent / "data"
                st.session_state.rag_engine = RAGEngine(data_dir=str(data_dir))
                st.session_state.rag_engine.initialize_index()
                st.session_state.index_loaded = True
                st.success("✅ Research database loaded!")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Make sure PDFs are in the 'data' folder")

# Main content
st.markdown('<div class="main-header">🌱 essenceAI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">B2B Market Intelligence for Sustainable Food Innovation</div>', unsafe_allow_html=True)

# Input section
st.markdown("### 💡 Product Concept Analysis")

col1, col2 = st.columns([3, 1])

with col1:
    product_concept = st.text_area(
        "Describe your product concept",
        placeholder="Example: Precision fermented cheese targeting French gourmet market with focus on artisan quality and sustainability",
        height=100,
        help="Be specific about your product, target market, and unique value proposition"
    )

with col2:
    st.markdown("**Quick Examples:**")
    if st.button("🧀 PF Cheese", use_container_width=True):
        product_concept = "Precision fermented artisan cheese for European gourmet market"
    if st.button("🍔 Plant Burger", use_container_width=True):
        product_concept = "Plant-based burger for fast-food chains emphasizing taste"
    if st.button("🌊 Algae Protein", use_container_width=True):
        product_concept = "Algae-based protein powder for health-conscious athletes"

analyze_button = st.button("🚀 Analyze Market", type="primary", use_container_width=True)

if analyze_button and product_concept:

    # Create tabs for different analyses
    tab1, tab2, tab3 = st.tabs(["📊 Competitor Intelligence", "🧠 Marketing Strategy", "🔬 Research Insights"])

    with tab1:
        st.markdown("### 🏢 Real-Time Competitor Analysis")

        with st.spinner("Fetching live market data..."):
            try:
                # Initialize competitor intelligence
                comp_intel = CompetitorIntelligence()

                # Get competitor data
                df = comp_intel.get_data(category, query=product_concept)

                if not df.empty:
                    # Display metrics
                    col1, col2, col3, col4 = st.columns(4)

                    stats = comp_intel.get_market_stats(category)

                    with col1:
                        st.metric("Avg Price/kg", f"${stats['avg_price_per_kg']}")
                    with col2:
                        st.metric("Avg CO₂/kg", f"{stats['avg_co2_emission']} kg")
                    with col3:
                        st.metric("Competitors", stats['competitor_count'])
                    with col4:
                        st.metric("Price Range", f"${stats['price_range']['min']}-${stats['price_range']['max']}")

                    st.markdown("---")

                    # Competitor table
                    st.markdown("#### 📋 Competitor Landscape")
                    st.dataframe(
                        df[['Company', 'Product', 'Price_per_kg', 'CO2_Emission_kg', 'Marketing_Claim']],
                        use_container_width=True,
                        hide_index=True
                    )

                    # Visualizations
                    col1, col2 = st.columns(2)

                    with col1:
                        # Price comparison
                        fig_price = px.bar(
                            df,
                            x='Company',
                            y='Price_per_kg',
                            title='Price Comparison ($/kg)',
                            color='Price_per_kg',
                            color_continuous_scale='Viridis'
                        )
                        fig_price.update_layout(showlegend=False)
                        st.plotly_chart(fig_price, use_container_width=True)

                    with col2:
                        # CO2 comparison
                        fig_co2 = px.bar(
                            df,
                            x='Company',
                            y='CO2_Emission_kg',
                            title='CO₂ Emissions (kg/kg product)',
                            color='CO2_Emission_kg',
                            color_continuous_scale='RdYlGn_r'
                        )
                        fig_co2.update_layout(showlegend=False)
                        st.plotly_chart(fig_co2, use_container_width=True)

                    # Price vs CO2 scatter
                    fig_scatter = px.scatter(
                        df,
                        x='CO2_Emission_kg',
                        y='Price_per_kg',
                        size='Price_per_kg',
                        color='Company',
                        hover_data=['Product', 'Marketing_Claim'],
                        title='Price vs Environmental Impact',
                        labels={'CO2_Emission_kg': 'CO₂ Emissions (kg)', 'Price_per_kg': 'Price ($/kg)'}
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)

                else:
                    st.warning("No competitor data available. Check API configuration.")

            except Exception as e:
                st.error(f"Error fetching competitor data: {str(e)}")

    with tab2:
        st.markdown("### 🎯 AI-Powered Marketing Strategy")

        if not st.session_state.index_loaded:
            st.warning("⚠️ Research database not loaded. Click 'Initialize Research Database' in the sidebar.")
        else:
            with st.spinner("Analyzing research papers for marketing insights..."):
                try:
                    rag_engine = st.session_state.rag_engine

                    # Get marketing strategy
                    if segment:
                        strategy, citations = rag_engine.get_marketing_strategy(
                            product_concept,
                            category,
                            segment
                        )

                        # Display strategy
                        st.markdown("#### 📝 Recommended Strategy")
                        st.markdown(f"**Target Segment:** {segment}")
                        st.info(strategy)
                    else:
                        # General strategy without segment targeting
                        strategy, citations = rag_engine.get_general_strategy(
                            product_concept,
                            category
                        )

                        # Display strategy
                        st.markdown("#### 📝 General Marketing Strategy")
                        st.info(strategy)
                        st.info("💡 **Tip:** Enable 'segment-specific insights' in the sidebar for targeted psychological strategies based on consumer research.")

                    # Display citations
                    st.markdown("#### 📚 Scientific Sources")

                    with st.expander("🔍 View Research Citations", expanded=True):
                        if citations:
                            for cite in citations:
                                st.markdown(f"""
                                <div class="citation-box">
                                    <strong>Source {cite['source_id']}:</strong> {cite['file_name']}<br>
                                    <strong>Page:</strong> {cite['page']} |
                                    <strong>Relevance:</strong> {cite['relevance_score']}<br>
                                    <em>"{cite['excerpt']}"</em>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No specific citations available for this query.")

                    # Segment explanation (only if segment is selected)
                    if segment:
                        st.markdown("---")
                        st.markdown("#### 🧠 Understanding Your Target Segment")

                        segment_info = {
                            "High Essentialist": {
                                "description": "Consumers who believe food categories have an immutable 'essence'",
                                "key_insight": "More likely to accept PBMAs if they successfully mimic sensory properties",
                                "strategy": "Emphasize sensory mimicry: 'Tastes like real meat', 'Juicy texture'"
                            },
                            "Skeptic": {
                                "description": "Low essentialists who value naturalness and origins",
                                "key_insight": "Reject products perceived as 'processed' or 'fake'",
                                "strategy": "Emphasize clean ingredients, natural origins, avoid uncanny comparisons"
                            },
                            "Non-Consumer": {
                                "description": "Neophobic consumers unfamiliar with alternatives",
                                "key_insight": "Fear of unfamiliar/processed foods",
                                "strategy": "Focus on familiar contexts, ease of use, downplay processing"
                            }
                        }

                        info = segment_info[segment]
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.markdown(f"**Description:**\n{info['description']}")
                        with col2:
                            st.markdown(f"**Key Insight:**\n{info['key_insight']}")
                        with col3:
                            st.markdown(f"**Strategy:**\n{info['strategy']}")

                except Exception as e:
                    st.error(f"Error generating strategy: {str(e)}")

    with tab3:
        st.markdown("### 🔬 Consumer Research Insights")

        if not st.session_state.index_loaded:
            st.warning("⚠️ Research database not loaded. Click 'Initialize Research Database' in the sidebar.")
        else:
            with st.spinner("Extracting insights from research papers..."):
                try:
                    rag_engine = st.session_state.rag_engine

                    # Get consumer insights
                    insights, citations = rag_engine.get_consumer_insights(category)

                    st.markdown("#### 📊 Key Findings")
                    st.success(insights)

                    # Citations
                    with st.expander("📚 Research Sources"):
                        if citations:
                            for cite in citations:
                                st.markdown(f"**{cite['file_name']}** (Page {cite['page']}) - Relevance: {cite['relevance_score']}")
                                st.caption(cite['excerpt'])
                                st.markdown("---")

                except Exception as e:
                    st.error(f"Error extracting insights: {str(e)}")

elif analyze_button:
    st.warning("⚠️ Please enter a product concept to analyze.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #64748b; padding: 2rem;'>
    <strong>essenceAI</strong> - Powered by OpenAI GPT-4o, LlamaIndex, and Tavily<br>
    Built for Hack the Fork 2025 🌱
</div>
""", unsafe_allow_html=True)
