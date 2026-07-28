"""
N100 Financial Intelligence Platform - Streamlit Dashboard
Day 22: Main app scaffold with sidebar navigation
"""

import streamlit as st
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Page configuration
st.set_page_config(
    page_title="Nifty 100 Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .sector-color-1 { color: #1f77b4; }
    .sector-color-2 { color: #ff7f0e; }
    .sector-color-3 { color: #2ca02c; }
    .sector-color-4 { color: #d62728; }
    .sector-color-5 { color: #9467bd; }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Sidebar Navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/200x50?text=Nifty100", use_column_width=True)
        
        st.markdown("---")
        st.subheader("📱 Navigation")
        
        page = st.radio(
            "Select Screen",
            [
                "🏠 Home",
                "👤 Company Profile",
                "🔍 Screener",
                "📊 Peer Comparison",
                "📈 Trend Analysis",
                "🏭 Sector Analysis",
                "💰 Capital Allocation",
                "📄 Annual Reports"
            ],
            key="nav_radio"
        )
        
        st.markdown("---")
        st.subheader("⚙️ Settings")
        
        debug_mode = st.checkbox("Debug Mode", value=False)
        
        st.markdown("---")
        st.info("📊 N100 Financial Intelligence Platform\nVersion 1.0 | Sprint 4")

    # Route to pages
    pages = {
        "🏠 Home": "pages.page_01_home",
        "👤 Company Profile": "pages.page_02_profile",
        "🔍 Screener": "pages.page_03_screener",
        "📊 Peer Comparison": "pages.page_04_peer",
        "📈 Trend Analysis": "pages.page_05_trends",
        "🏭 Sector Analysis": "pages.page_06_sector",
        "💰 Capital Allocation": "pages.page_07_allocation",
        "📄 Annual Reports": "pages.page_08_reports"
    }
    
    if page in pages:
        try:
            module_name = pages[page]
            exec(f"from {module_name} import app as page_app")
            page_app()
        except Exception as e:
            st.error(f"Error loading page: {str(e)}")
            if debug_mode:
                st.write(f"Module: {module_name}")
                import traceback
                st.write(traceback.format_exc())
    else:
        st.warning("Page not found")


if __name__ == "__main__":
    main()
