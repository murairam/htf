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

from competitor_data import OptimizedCompetitorIntelligence
from rag_engine_optimized import OptimizedRAGEngine

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
if 'auto_init_attempted' not in st.session_state:
    st.session_state.auto_init_attempted = False

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/200x80/667eea/ffffff?text=essenceAI", width='stretch')

    st.markdown("### 🎯 Domain Selection")
    st.markdown("*Optional: Focus on specific domain*")

    use_category = st.checkbox(
        "Enable domain-specific analysis",
        value=False,
        help="Focus analysis on a specific sustainable food sector"
    )

    if use_category:
        category = st.selectbox(
            "Select Innovation Domain",
            ["Precision Fermentation", "Plant-Based", "Algae"],
            help="Choose the sustainable food sector to analyze"
        )
    else:
        category = None

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
    if st.button("🔄 Initialize Research Database", width='stretch'):
        with st.spinner("Loading research papers..."):
            try:
                data_dir = Path(__file__).parent.parent / "data"
                st.session_state.rag_engine = OptimizedRAGEngine(data_dir=str(data_dir))
                st.session_state.rag_engine.initialize_index()
                st.session_state.index_loaded = True
                st.success("✅ Research database loaded! (Using optimized engine)")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Make sure PDFs are in the 'data' folder")

# Main content
st.markdown('<div class="main-header">🌱 essenceAI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">B2B Market Intelligence for Sustainable Food Innovation</div>', unsafe_allow_html=True)

# Input section
st.markdown("### 💡 Product Concept Analysis")

product_concept = st.text_area(
    "Describe your product concept",
    placeholder="Example: Precision fermented cheese targeting French gourmet market with focus on artisan quality and sustainability",
    height=100,
    help="Be specific about your product, target market, and unique value proposition"
)

analyze_button = st.button("🚀 Analyze Market", type="primary", use_container_width=True)

if analyze_button and product_concept:

# Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Competitor Intelligence", "🧠 Marketing Strategy", "🔬 Research Insights", "🤖 AI Agent Analysis"])

    with tab1:
        st.markdown("### 🏢 Real-Time Competitor Analysis")

        with st.spinner("Fetching live market data..."):
            try:
                # Initialize optimized competitor intelligence (database disabled for fresh results)
                comp_intel = OptimizedCompetitorIntelligence(use_database=False)

                # Get competitor data - always fetch fresh data
                competitors = comp_intel.get_competitors(
                    product_concept=product_concept,
                    category=category if category else None,
                    max_results=10,
                    use_cache=False  # Always fetch fresh data
                )

                # Convert to DataFrame
                if competitors:
                    df = pd.DataFrame(competitors)
                    # Rename columns to match expected format - handle both EUR and USD
                    rename_map = {}
                    if 'Price (€/kg)' in df.columns:
                        rename_map['Price (€/kg)'] = 'Price_per_kg'
                        currency_symbol = '€'
                    elif 'Price ($/kg)' in df.columns:
                        rename_map['Price ($/kg)'] = 'Price_per_kg'
                        currency_symbol = '$'
                    else:
                        currency_symbol = '€'  # Default to EUR

                    if 'CO₂ (kg)' in df.columns:
                        rename_map['CO₂ (kg)'] = 'CO2_Emission_kg'
                    if 'Marketing Claim' in df.columns:
                        rename_map['Marketing Claim'] = 'Marketing_Claim'

                    if rename_map:
                        df = df.rename(columns=rename_map)
                else:
                    df = pd.DataFrame()

                if not df.empty and 'Price_per_kg' in df.columns and 'CO2_Emission_kg' in df.columns:
                    # Display metrics
                    col1, col2, col3, col4 = st.columns(4)

                    # Calculate stats from DataFrame with error handling
                    try:
                        # Filter out None/NaN values for calculations
                        valid_prices = df['Price_per_kg'].dropna()
                        valid_co2 = df['CO2_Emission_kg'].dropna()

                        # Calculate data completeness
                        price_completeness = len(valid_prices) / len(df) * 100 if len(df) > 0 else 0
                        co2_completeness = len(valid_co2) / len(df) * 100 if len(df) > 0 else 0

                        with col1:
                            if len(valid_prices) > 0:
                                avg_price = round(valid_prices.mean(), 2)
                                st.metric("Avg Price/kg", f"{currency_symbol}{avg_price}",
                                         delta=f"{len(valid_prices)}/{len(df)} available" if len(valid_prices) < len(df) else None)
                            else:
                                st.metric("Avg Price/kg", "N/A", delta="No data available")

                        with col2:
                            if len(valid_co2) > 0:
                                avg_co2 = round(valid_co2.mean(), 2)
                                st.metric("Avg CO₂/kg", f"{avg_co2} kg",
                                         delta=f"{len(valid_co2)}/{len(df)} available" if len(valid_co2) < len(df) else None)
                            else:
                                st.metric("Avg CO₂/kg", "N/A", delta="No data available")

                        with col3:
                            st.metric("Competitors Found", len(df))

                        with col4:
                            if len(valid_prices) > 0:
                                price_range = f"{currency_symbol}{round(valid_prices.min(), 2)}-{currency_symbol}{round(valid_prices.max(), 2)}"
                                st.metric("Price Range", price_range)
                            else:
                                st.metric("Price Range", "N/A")

                        # Show data quality warning if needed
                        if price_completeness < 50 or co2_completeness < 50:
                            st.warning(f"⚠️ Data completeness: Price {price_completeness:.0f}%, CO₂ {co2_completeness:.0f}%. Some competitors may not have complete information available from public sources.")
                        elif price_completeness < 100 or co2_completeness < 100:
                            st.info(f"ℹ️ Data completeness: Price {price_completeness:.0f}%, CO₂ {co2_completeness:.0f}%. Click source links for more details.")
                    except Exception as e:
                        st.error(f"Error calculating metrics: {str(e)}")

                    st.markdown("---")

                    # Competitor table
                    st.markdown("#### 📋 Competitor Landscape")

                    # Display only relevant columns (removed Price and CO2 as they're rarely available)
                    display_columns = ['Company', 'Product', 'Marketing_Claim']
                    if 'Source' in df.columns:
                        display_columns.append('Source')

                    display_df = df[display_columns].copy()

                    column_config = {}
                    if 'Source' in display_columns:
                        column_config["Source"] = st.column_config.LinkColumn(
                            "Source",
                            help="Click to view source for pricing and sustainability data",
                            display_text="🔗 View Details"
                        )

                    st.dataframe(
                        display_df,
                        width='stretch',
                        hide_index=True,
                        column_config=column_config
                    )

                    st.info("💡 **Tip:** Click 'View Details' links to find pricing and environmental impact data on competitor websites.")

                    # Visualizations - create with available data
                    if 'Price_per_kg' in df.columns and 'CO2_Emission_kg' in df.columns:
                        # Filter out rows with missing data for visualizations
                        viz_df_price = df.dropna(subset=['Price_per_kg'])
                        viz_df_co2 = df.dropna(subset=['CO2_Emission_kg'])
                        viz_df_both = df.dropna(subset=['Price_per_kg', 'CO2_Emission_kg'])

                        col1, col2 = st.columns(2)

                        with col1:
                            # Price comparison - show if we have any price data
                            if not viz_df_price.empty:
                                fig_price = px.bar(
                                    viz_df_price,
                                    x='Company',
                                    y='Price_per_kg',
                                    title=f'Price Comparison ({currency_symbol}/kg) - {len(viz_df_price)} companies',
                                    color='Price_per_kg',
                                    color_continuous_scale='Viridis'
                                )
                                fig_price.update_layout(showlegend=False)
                                st.plotly_chart(fig_price, use_container_width=True)
                            else:
                                st.info("📊 Price data not available for visualization. Check source links for pricing information.")

                        with col2:
                            # CO2 comparison - show if we have any CO2 data
                            if not viz_df_co2.empty:
                                fig_co2 = px.bar(
                                    viz_df_co2,
                                    x='Company',
                                    y='CO2_Emission_kg',
                                    title=f'CO₂ Emissions (kg/kg product) - {len(viz_df_co2)} companies',
                                    color='CO2_Emission_kg',
                                    color_continuous_scale='RdYlGn_r'
                                )
                                fig_co2.update_layout(showlegend=False)
                                st.plotly_chart(fig_co2, use_container_width=True)
                            else:
                                st.info("📊 CO₂ data not available for visualization. Environmental impact data may not be publicly disclosed.")

                        # Price vs CO2 scatter - only if we have both
                        if not viz_df_both.empty:
                            hover_data_cols = ['Product']
                            if 'Marketing_Claim' in viz_df_both.columns:
                                hover_data_cols.append('Marketing_Claim')

                            fig_scatter = px.scatter(
                                viz_df_both,
                                x='CO2_Emission_kg',
                                y='Price_per_kg',
                                size='Price_per_kg',
                                color='Company',
                                hover_data=hover_data_cols,
                                title=f'Price vs Environmental Impact - {len(viz_df_both)} companies with complete data',
                                labels={'CO2_Emission_kg': 'CO₂ Emissions (kg)', 'Price_per_kg': f'Price ({currency_symbol}/kg)'}
                            )
                            st.plotly_chart(fig_scatter, use_container_width=True)
                        else:
                            st.info("📊 Combined price and CO₂ visualization requires both metrics. Visit source links for complete information.")
                    else:
                        st.warning("⚠️ Missing required columns for visualizations.")

                else:
                    st.warning("No competitor data available. Check API configuration.")

            except Exception as e:
                st.error(f"Error fetching competitor data: {str(e)}")

    with tab2:
        st.markdown("### 🎯 AI-Powered Marketing Strategy")

        # Auto-initialize research database on first access
        if not st.session_state.index_loaded:
            with st.spinner("🔄 Loading research database... (This happens once on first use)"):
                try:
                    data_dir = Path(__file__).parent.parent / "data"
                    st.session_state.rag_engine = OptimizedRAGEngine(data_dir=str(data_dir))
                    st.session_state.rag_engine.initialize_index()
                    st.session_state.index_loaded = True
                    st.success("✅ Research database loaded successfully!")
                except Exception as e:
                    st.error(f"❌ Failed to load research database: {str(e)}")
                    st.info("💡 Make sure PDF research papers are in the 'data' folder.")

        if st.session_state.index_loaded:
            with st.spinner("Analyzing research papers for marketing insights..."):
                try:
                    rag_engine = st.session_state.rag_engine

                    # Get marketing strategy (always with use_cache=False for dynamic results)
                    if segment and category:
                        # Segment-specific + category-specific
                        strategy, citations = rag_engine.get_marketing_strategy(
                            product_concept,
                            category,
                            segment,
                            use_cache=False
                        )

                        st.markdown("#### 📝 Recommended Strategy")
                        st.markdown(f"**Domain:** {category} | **Target Segment:** {segment}")
                        st.info(strategy)
                    elif segment and not category:
                        # Segment-specific but general domain
                        strategy, citations = rag_engine.get_segment_strategy(
                            product_concept,
                            segment,
                            use_cache=False
                        )

                        st.markdown("#### 📝 Recommended Strategy")
                        st.markdown(f"**Target Segment:** {segment} | **Domain:** All Sustainable Food")
                        st.info(strategy)
                    elif category and not segment:
                        # Category-specific but general segment
                        strategy, citations = rag_engine.get_general_strategy(
                            product_concept,
                            category,
                            use_cache=False
                        )

                        st.markdown("#### 📝 General Marketing Strategy")
                        st.markdown(f"**Domain:** {category}")
                        st.info(strategy)
                        st.info("💡 **Tip:** Enable 'segment-specific insights' for targeted psychological strategies.")
                    else:
                        # Fully general - no category, no segment
                        strategy, citations = rag_engine.get_universal_strategy(
                            product_concept,
                            use_cache=False
                        )

                        st.markdown("#### 📝 Universal Marketing Strategy")
                        st.markdown("**Domain:** All Sustainable Food | **Audience:** General")
                        st.info(strategy)
                        st.info("💡 **Tip:** Enable domain and segment filters for more targeted insights.")

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

        # Auto-initialize research database on first access
        if not st.session_state.index_loaded:
            with st.spinner("🔄 Loading research database... (This happens once on first use)"):
                try:
                    data_dir = Path(__file__).parent.parent / "data"
                    st.session_state.rag_engine = OptimizedRAGEngine(data_dir=str(data_dir))
                    st.session_state.rag_engine.initialize_index()
                    st.session_state.index_loaded = True
                    st.success("✅ Research database loaded successfully!")
                except Exception as e:
                    st.error(f"❌ Failed to load research database: {str(e)}")
                    st.info("💡 Make sure PDF research papers are in the 'data' folder.")

        if st.session_state.index_loaded:
            with st.spinner("Extracting insights from research papers..."):
                try:
                    rag_engine = st.session_state.rag_engine

                    # Get consumer insights (with product context for dynamic results)
                    if category:
                        insights, citations = rag_engine.get_consumer_insights(
                            category,
                            product_context=product_concept,
                            use_cache=False
                        )
                    else:
                        insights, citations = rag_engine.get_consumer_insights(
                            "sustainable food alternatives",
                            product_context=product_concept,
                            use_cache=False
                        )

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

    with tab4:
        st.markdown("### 🤖 AI Agent Orchestration")
        st.info("💡 **New Feature**: Use our AI agent system for comprehensive, multi-step analysis with advanced capabilities.")

        # Agent mode selection
        col1, col2 = st.columns([2, 1])

        with col1:
            agent_mode = st.radio(
                "Select Analysis Mode",
                ["🎯 Full Orchestrated Analysis", "🔧 Individual Agent Tasks", "📊 Agent Dashboard"],
                help="Choose how you want to interact with the agent system"
            )

        with col2:
            st.markdown("**Agent System Status**")
            # Import agent orchestrator
            try:
                from agents.orchestrator import AgentOrchestrator

                # Initialize orchestrator in session state
                if 'orchestrator' not in st.session_state:
                    data_dir = Path(__file__).parent.parent / "data"
                    st.session_state.orchestrator = AgentOrchestrator(
                        data_dir=str(data_dir),
                        persist_dir=str(Path(__file__).parent.parent / ".storage")
                    )

                orchestrator = st.session_state.orchestrator
                agent_status = orchestrator.get_agent_status()

                st.markdown(f"✅ Research: {'Ready' if agent_status['research_initialized'] else 'Not Initialized'}")
                st.markdown(f"✅ Competitor: Ready")
                st.markdown(f"✅ Marketing: Ready")

            except Exception as e:
                st.error(f"Error loading agents: {str(e)}")
                agent_mode = None

        st.markdown("---")

        # Full Orchestrated Analysis Mode
        if agent_mode == "🎯 Full Orchestrated Analysis":
            st.markdown("#### 🎯 Complete Market Intelligence Workflow")
            st.markdown("""
            This mode executes a comprehensive analysis using all agents in sequence:
            1. **Competitor Agent**: Gathers real-time market data
            2. **Research Agent**: Extracts scientific insights from papers
            3. **Marketing Agent**: Generates targeted strategy based on all data
            """)

            # Initialize research option
            col1, col2 = st.columns([3, 1])
            with col1:
                if not agent_status.get('research_initialized', False):
                    st.warning("⚠️ Research agent not initialized. Initialize to include research insights in analysis.")
            with col2:
                if st.button("🔄 Initialize Research", disabled=agent_status.get('research_initialized', False)):
                    with st.spinner("Loading research database..."):
                        try:
                            success = orchestrator.initialize_research()
                            if success:
                                st.success("✅ Research database loaded!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to initialize research database")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

            # Execute full analysis
            if st.button("🚀 Execute Full Analysis", type="primary", use_container_width=True):
                with st.spinner("🤖 Agents working on your analysis..."):
                    try:
                        # Execute orchestrated workflow
                        result = orchestrator.execute_full_analysis(
                            product_description=product_concept,
                            domain=category if category else None,
                            segment=segment if segment else None
                        )

                        if result['status'] == 'success':
                            st.success("✅ Analysis completed successfully!")

                            analysis_data = result['data']

                            # Display workflow steps
                            with st.expander("📋 Workflow Execution Details", expanded=False):
                                workflow = result['workflow']
                                for i, step in enumerate(workflow['steps'], 1):
                                    status_icon = "✅" if step['status'] == 'success' else "⚠️" if step['status'] == 'skipped' else "❌"
                                    st.markdown(f"{status_icon} **Step {i}**: {step['agent'].title()} Agent - {step['status']}")

                            # Competitor Intelligence Results
                            st.markdown("---")
                            st.markdown("### 📊 Competitor Intelligence")

                            comp_data = analysis_data.get('competitor_intelligence', {})
                            if comp_data and 'competitors' in comp_data:
                                competitors = comp_data['competitors']
                                stats = comp_data.get('statistics', {})

                                # Metrics
                                if stats:
                                    col1, col2, col3 = st.columns(3)
                                    with col1:
                                        if 'price_stats' in stats:
                                            st.metric("Avg Price/kg", f"${stats['price_stats']['avg']:.2f}")
                                    with col2:
                                        if 'co2_stats' in stats:
                                            st.metric("Avg CO₂/kg", f"{stats['co2_stats']['avg']:.2f} kg")
                                    with col3:
                                        st.metric("Competitors Found", stats.get('total_competitors', 0))

                                # Competitor table
                                if competitors:
                                    df = pd.DataFrame(competitors)
                                    st.dataframe(df, use_container_width=True, hide_index=True)
                            else:
                                st.info("No competitor data available")

                            # Research Insights Results
                            st.markdown("---")
                            st.markdown("### 🔬 Research Insights")

                            research_data = analysis_data.get('research_insights')
                            if research_data and 'answer' in research_data:
                                st.success(research_data['answer'])

                                # Citations
                                if 'citations' in research_data and research_data['citations']:
                                    with st.expander("📚 Scientific Sources", expanded=False):
                                        for cite in research_data['citations']:
                                            st.markdown(f"""
                                            <div class="citation-box">
                                                <strong>{cite['file_name']}</strong> (Page {cite['page']})<br>
                                                <em>"{cite['excerpt'][:200]}..."</em>
                                            </div>
                                            """, unsafe_allow_html=True)
                            else:
                                st.info("Research insights not available (initialize research agent to enable)")

                            # Marketing Strategy Results
                            st.markdown("---")
                            st.markdown("### 🎯 Marketing Strategy")

                            marketing_data = analysis_data.get('marketing_strategy')
                            if marketing_data:
                                # Positioning
                                if 'positioning' in marketing_data:
                                    st.markdown("#### Positioning Strategy")
                                    pos = marketing_data['positioning']
                                    col1, col2 = st.columns(2)
                                    with col1:
                                        st.markdown(f"**Target Audience:** {pos.get('target_audience', 'N/A')}")
                                        st.markdown(f"**Category:** {pos.get('category', 'N/A')}")
                                    with col2:
                                        st.markdown(f"**Point of Difference:** {pos.get('point_of_difference', 'N/A')}")

                                # Key Messages
                                if 'key_messages' in marketing_data:
                                    st.markdown("#### Key Messages")
                                    for msg in marketing_data['key_messages']:
                                        st.markdown(f"• {msg}")

                                # Tactics
                                if 'tactics' in marketing_data:
                                    st.markdown("#### Recommended Tactics")
                                    tactics_df = pd.DataFrame(marketing_data['tactics'])
                                    st.dataframe(tactics_df, use_container_width=True, hide_index=True)
                            else:
                                st.info("Marketing strategy not available (specify target segment to enable)")

                        else:
                            st.error(f"❌ Analysis failed: {result.get('message', 'Unknown error')}")

                    except Exception as e:
                        st.error(f"Error during analysis: {str(e)}")
                        import traceback
                        with st.expander("Error Details"):
                            st.code(traceback.format_exc())

        # Individual Agent Tasks Mode
        elif agent_mode == "🔧 Individual Agent Tasks":
            st.markdown("#### 🔧 Execute Individual Agent Tasks")
            st.markdown("Run specific agents for targeted analysis.")

            agent_choice = st.selectbox(
                "Select Agent",
                ["Competitor Agent", "Research Agent", "Marketing Agent"],
                help="Choose which agent to execute"
            )

            if agent_choice == "Competitor Agent":
                st.markdown("##### 📊 Competitor Agent Tasks")

                task_type = st.radio(
                    "Task Type",
                    ["Basic Competitor Analysis", "Pricing Analysis", "Sustainability Analysis", "Market Gap Analysis"],
                    horizontal=True
                )

                if st.button("Execute Competitor Task", type="primary"):
                    with st.spinner(f"🤖 Executing {task_type}..."):
                        try:
                            if task_type == "Basic Competitor Analysis":
                                result = orchestrator.competitor_agent.execute({
                                    'product_description': product_concept,
                                    'domain': category if category else None,
                                    'max_competitors': 10
                                })
                            elif task_type == "Pricing Analysis":
                                result = orchestrator.competitor_agent.analyze_pricing(
                                    product_concept,
                                    category if category else None
                                )
                            elif task_type == "Sustainability Analysis":
                                result = orchestrator.competitor_agent.analyze_sustainability(
                                    product_concept,
                                    category if category else None
                                )
                            elif task_type == "Market Gap Analysis":
                                result = orchestrator.competitor_agent.find_market_gaps(
                                    product_concept,
                                    category if category else None
                                )

                            if result['status'] == 'success':
                                st.success("✅ Task completed!")
                                st.json(result['data'])
                            else:
                                st.error(f"❌ Task failed: {result.get('message', 'Unknown error')}")

                        except Exception as e:
                            st.error(f"Error: {str(e)}")

            elif agent_choice == "Research Agent":
                st.markdown("##### 🔬 Research Agent Tasks")

                if not agent_status.get('research_initialized', False):
                    st.warning("⚠️ Research agent not initialized. Click 'Initialize Research' button above.")
                else:
                    task_type = st.radio(
                        "Task Type",
                        ["Consumer Acceptance Analysis", "Barrier Identification", "Marketing Insights"],
                        horizontal=True
                    )

                    if st.button("Execute Research Task", type="primary"):
                        with st.spinner(f"🤖 Executing {task_type}..."):
                            try:
                                if task_type == "Consumer Acceptance Analysis":
                                    result = orchestrator.research_agent.analyze_consumer_acceptance(
                                        category if category else "sustainable food alternatives",
                                        segment if segment else None
                                    )
                                elif task_type == "Barrier Identification":
                                    result = orchestrator.research_agent.identify_barriers(
                                        category if category else "sustainable food alternatives"
                                    )
                                elif task_type == "Marketing Insights":
                                    if segment:
                                        result = orchestrator.research_agent.get_marketing_insights(
                                            category if category else "sustainable food alternatives",
                                            segment
                                        )
                                    else:
                                        st.error("Please select a target segment for marketing insights")
                                        result = None

                                if result and result['status'] == 'success':
                                    st.success("✅ Task completed!")
                                    data = result['data']
                                    st.markdown(data.get('answer', 'No answer available'))

                                    if 'citations' in data and data['citations']:
                                        with st.expander("📚 Citations"):
                                            for cite in data['citations']:
                                                st.markdown(f"**{cite['file_name']}** (Page {cite['page']})")
                                                st.caption(cite['excerpt'])
                                elif result:
                                    st.error(f"❌ Task failed: {result.get('message', 'Unknown error')}")

                            except Exception as e:
                                st.error(f"Error: {str(e)}")

            elif agent_choice == "Marketing Agent":
                st.markdown("##### 🎯 Marketing Agent Tasks")

                if not segment:
                    st.warning("⚠️ Please select a target consumer segment in the sidebar.")
                else:
                    task_type = st.radio(
                        "Task Type",
                        ["Generate Strategy", "Compare All Segments"],
                        horizontal=True
                    )

                    if st.button("Execute Marketing Task", type="primary"):
                        with st.spinner(f"🤖 Executing {task_type}..."):
                            try:
                                if task_type == "Generate Strategy":
                                    result = orchestrator.marketing_agent.execute({
                                        'product_description': product_concept,
                                        'segment': segment,
                                        'domain': category if category else None
                                    })
                                elif task_type == "Compare All Segments":
                                    result = orchestrator.marketing_agent.compare_segments(
                                        product_concept,
                                        category if category else None
                                    )

                                if result['status'] == 'success':
                                    st.success("✅ Task completed!")

                                    data = result['data']

                                    if task_type == "Generate Strategy":
                                        # Display strategy details
                                        if 'positioning' in data:
                                            st.markdown("#### Positioning")
                                            st.json(data['positioning'])

                                        if 'key_messages' in data:
                                            st.markdown("#### Key Messages")
                                            for msg in data['key_messages']:
                                                st.markdown(f"• {msg}")

                                        if 'tactics' in data:
                                            st.markdown("#### Tactics")
                                            st.dataframe(pd.DataFrame(data['tactics']), use_container_width=True)
                                    else:
                                        # Segment comparison
                                        for seg, strategy in data.items():
                                            with st.expander(f"📊 {seg} Strategy"):
                                                st.json(strategy)
                                else:
                                    st.error(f"❌ Task failed: {result.get('message', 'Unknown error')}")

                            except Exception as e:
                                st.error(f"Error: {str(e)}")

        # Agent Dashboard Mode
        elif agent_mode == "📊 Agent Dashboard":
            st.markdown("#### 📊 Agent System Dashboard")

            # Agent Status
            st.markdown("### Agent Status")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("**🔬 Research Agent**")
                research_status = agent_status.get('research', {})
                st.markdown(f"Status: {'✅ Initialized' if agent_status.get('research_initialized') else '⚠️ Not Initialized'}")
                st.markdown(f"Tasks: {research_status.get('tasks_completed', 0)} completed")

            with col2:
                st.markdown("**📊 Competitor Agent**")
                comp_status = agent_status.get('competitor', {})
                st.markdown(f"Status: ✅ Ready")
                st.markdown(f"Tasks: {comp_status.get('tasks_completed', 0)} completed")

            with col3:
                st.markdown("**🎯 Marketing Agent**")
                marketing_status = agent_status.get('marketing', {})
                st.markdown(f"Status: ✅ Ready")
                st.markdown(f"Tasks: {marketing_status.get('tasks_completed', 0)} completed")

            # Workflow History
            st.markdown("---")
            st.markdown("### 📜 Workflow History")

            history = orchestrator.get_workflow_history()

            if history:
                st.markdown(f"Total workflows executed: **{len(history)}**")

                for i, workflow in enumerate(reversed(history[-5:]), 1):  # Show last 5
                    with st.expander(f"Workflow #{workflow['id']} - {workflow['product'][:50]}..."):
                        st.markdown(f"**Product:** {workflow['product']}")
                        st.markdown(f"**Domain:** {workflow.get('domain', 'N/A')}")
                        st.markdown(f"**Segment:** {workflow.get('segment', 'N/A')}")

                        st.markdown("**Steps:**")
                        for step in workflow['steps']:
                            status_icon = "✅" if step['status'] == 'success' else "⚠️" if step['status'] == 'skipped' else "❌"
                            st.markdown(f"{status_icon} {step['agent'].title()} Agent - {step['status']}")
            else:
                st.info("No workflows executed yet. Run a full analysis to see history here.")

            # Clear History
            if st.button("🗑️ Clear History", type="secondary"):
                orchestrator.clear_history()
                st.success("History cleared!")
                st.rerun()


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
