"""
Sector Analysis Screen - Sector-Level Analytics
Day 25: Sector dropdown, bubble chart, median KPI bar chart
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sqlite3
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from dashboard.utils.db import (
    load_sectors, load_sector_companies, load_sector_medians, get_available_years
)


def get_sector_bubble_data(sector_id: str, year: int) -> pd.DataFrame:
    """Get bubble chart data: Revenue vs ROE, size = Market Cap"""
    DB_PATH = 'c:/bluestock-mf-capstone/n100/db/nifty100.db'
    conn = sqlite3.connect(DB_PATH)
    
    query = """
    SELECT 
        c.company_id,
        c.company_name,
        c.market_cap_inr,
        pl.revenue_cr,
        fr.roe
    FROM companies c
    LEFT JOIN profitandloss pl ON c.company_id = pl.company_id AND pl.year = ?
    LEFT JOIN financial_ratios fr ON c.company_id = fr.company_id AND fr.year = ?
    WHERE c.sector_id = ?
    AND pl.revenue_cr IS NOT NULL
    AND fr.roe IS NOT NULL
    """
    
    df = pd.read_sql_query(query, conn, params=(year, year, sector_id))
    conn.close()
    
    return df


def get_sector_kpi_medians(sector_id: str, year: int) -> pd.DataFrame:
    """Get median KPIs for all companies in sector"""
    DB_PATH = 'c:/bluestock-mf-capstone/n100/db/nifty100.db'
    conn = sqlite3.connect(DB_PATH)
    
    query = """
    SELECT 
        fr.roe,
        fr.roce,
        fr.opm,
        fr.npm,
        fr.pe_ratio,
        fr.pb_ratio,
        fr.debt_to_equity,
        fr.dividend_yield
    FROM financial_ratios fr
    JOIN companies c ON fr.company_id = c.company_id
    WHERE c.sector_id = ? AND fr.year = ?
    """
    
    df = pd.read_sql_query(query, conn, params=(sector_id, year))
    conn.close()
    
    return df


def app():
    """Sector Analysis screen main function"""
    st.title("🏭 Sector Analysis")
    
    # Sector selection
    sectors = load_sectors()
    
    if sectors.empty:
        st.error("No sector data available")
        return
    
    sector_names = sectors['sector_name'].tolist()
    
    selected_sector = st.selectbox(
        "Select Sector",
        sector_names,
        key="sector_analysis_select",
        placeholder="Choose a sector..."
    )
    
    if not selected_sector:
        st.info("📌 Select a sector to view analysis")
        return
    
    # Get sector ID
    sector_row = sectors[sectors['sector_name'] == selected_sector].iloc[0]
    sector_id = sector_row['sector_id']
    
    # Year selector
    available_years = get_available_years()
    selected_year = st.selectbox("Select Year", available_years, index=0, key="sector_year")
    
    st.markdown("---")
    st.subheader(f"📊 {selected_sector} - {selected_year}")
    
    # Get sector companies
    sector_companies = load_sector_companies(sector_id)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Companies", len(sector_companies))
    
    with col2:
        avg_market_cap = sector_companies['market_cap_inr'].mean() if not sector_companies.empty else 0
        st.metric("Avg Market Cap (Cr)", f"₹{avg_market_cap:,.0f}")
    
    with col3:
        total_market_cap = sector_companies['market_cap_inr'].sum() if not sector_companies.empty else 0
        st.metric("Total Market Cap (Cr)", f"₹{total_market_cap:,.0f}")
    
    with col4:
        st.metric("Companies Listed", len(sector_companies))
    
    st.markdown("---")
    
    # Bubble Chart: Revenue vs ROE, Size = Market Cap
    st.subheader("💹 Revenue vs ROE (Bubble Size = Market Cap)")
    
    bubble_data = get_sector_bubble_data(sector_id, int(selected_year))
    
    if not bubble_data.empty:
        fig = px.scatter(
            bubble_data,
            x='revenue_cr',
            y='roe',
            size='market_cap_inr',
            hover_name='company_name',
            title="",
            labels={
                'revenue_cr': 'Revenue (Cr)',
                'roe': 'ROE (%)',
                'market_cap_inr': 'Market Cap (Cr)'
            },
            color='roe',
            color_continuous_scale='Viridis',
            size_max=50
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No bubble chart data available")
    
    st.markdown("---")
    
    # Sector Median KPI Bar Chart
    st.subheader("📊 Sector Median KPIs")
    
    kpi_df = get_sector_kpi_medians(sector_id, int(selected_year))
    
    if not kpi_df.empty:
        medians = kpi_df.median()
        
        kpi_names = ['ROE (%)', 'ROCE (%)', 'OPM (%)', 'NPM (%)', 'P/E', 'P/B', 'D/E', 'Div Yield (%)']
        kpi_cols = ['roe', 'roce', 'opm', 'npm', 'pe_ratio', 'pb_ratio', 'debt_to_equity', 'dividend_yield']
        
        kpi_values = [medians.get(col, 0) for col in kpi_cols]
        
        fig = go.Figure(
            data=[go.Bar(
                x=kpi_names,
                y=kpi_values,
                marker=dict(
                    color=kpi_values,
                    colorscale='Viridis'
                ),
                text=[f"{v:.2f}" for v in kpi_values],
                textposition='auto',
                hovertemplate="<b>%{x}</b><br>Median: %{y:.2f}<extra></extra>"
            )]
        )
        
        fig.update_layout(
            title="",
            xaxis_title="Metric",
            yaxis_title="Value",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Summary stats
        st.markdown("---")
        st.subheader("📈 Summary Statistics")
        
        stats_data = {
            'Metric': kpi_names,
            'Median': [f"{v:.2f}" for v in kpi_values],
            'Mean': [f"{kpi_df[col].mean():.2f}" if col in kpi_df.columns else "N/A" for col in kpi_cols],
            'Min': [f"{kpi_df[col].min():.2f}" if col in kpi_df.columns else "N/A" for col in kpi_cols],
            'Max': [f"{kpi_df[col].max():.2f}" if col in kpi_df.columns else "N/A" for col in kpi_cols],
        }
        
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
    else:
        st.warning("No KPI data available for this sector")
    
    st.markdown("---")
    
    # Companies in Sector
    st.subheader("👥 Companies in Sector")
    
    if not sector_companies.empty:
        display_data = sector_companies[['company_name', 'market_cap_inr']].copy()
        display_data.columns = ['Company', 'Market Cap (Cr)']
        display_data = display_data.sort_values('Market Cap (Cr)', ascending=False)
        
        st.dataframe(display_data, use_container_width=True, hide_index=True)
    else:
        st.info("No companies in this sector")


if __name__ == "__main__":
    app()
