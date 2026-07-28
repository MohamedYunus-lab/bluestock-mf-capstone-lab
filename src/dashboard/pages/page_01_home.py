"""
Home Screen - KPI Overview & Market Summary
Day 23: 6 KPI tiles, sector donut chart, top 5 companies
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from dashboard.utils.db import (
    get_kpi_summary, get_sector_distribution, 
    get_top_companies_by_metric, get_available_years
)


def app():
    """Home screen main function"""
    st.title("📊 Nifty 100 Financial Analytics")
    
    # Year selector
    available_years = get_available_years()
    if available_years:
        selected_year = st.selectbox(
            "Select Year",
            available_years,
            index=0,
            key="home_year_selector"
        )
    else:
        selected_year = 2023
        st.warning("No data available in database")
    
    # Load KPI summary
    kpi_data = get_kpi_summary(selected_year)
    
    # KPI Section
    st.subheader("📈 Key Performance Indicators")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Average ROE (%)",
            f"{kpi_data.get('avg_roe', 0):.2f}" if kpi_data.get('avg_roe') else "N/A",
            delta="Portfolio Health",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "Median P/E Ratio",
            f"{kpi_data.get('median_pe', 0):.2f}" if kpi_data.get('median_pe') else "N/A",
            delta="Valuation Metric",
            delta_color="off"
        )
    
    with col3:
        st.metric(
            "Median D/E Ratio",
            f"{kpi_data.get('median_de', 0):.2f}" if kpi_data.get('median_de') else "N/A",
            delta="Leverage Health",
            delta_color="off"
        )
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.metric(
            "Total Companies",
            int(kpi_data.get('total_companies', 0)),
            delta="In Index",
            delta_color="off"
        )
    
    with col5:
        st.metric(
            "Debt-Free Count",
            int(kpi_data.get('debt_free_count', 0)),
            delta="Zero Leverage",
            delta_color="normal"
        )
    
    with col6:
        st.metric(
            "Avg Revenue (Cr)",
            f"₹{kpi_data.get('avg_revenue', 0):.0f}" if kpi_data.get('avg_revenue') else "N/A",
            delta="Scale Metric",
            delta_color="off"
        )
    
    # Charts Section
    st.markdown("---")
    st.subheader("📊 Market Overview")
    
    left_col, right_col = st.columns(2)
    
    # Sector Distribution Donut Chart
    with left_col:
        sector_data = get_sector_distribution(selected_year)
        
        if not sector_data.empty:
            fig_donut = go.Figure(
                data=[go.Pie(
                    labels=sector_data['sector_name'],
                    values=sector_data['count'],
                    hole=0.4,
                    marker=dict(
                        colors=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                               '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', '#aec7e8']
                    ),
                    hovertemplate="<b>%{label}</b><br>Companies: %{value}<extra></extra>"
                )]
            )
            fig_donut.update_layout(
                title="Sector Distribution",
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.warning("No sector data available")
    
    # Top 5 Companies by ROE
    with right_col:
        top_companies = get_top_companies_by_metric('roe', selected_year, limit=5)
        
        if not top_companies.empty:
            fig_bar = go.Figure(
                data=[go.Bar(
                    x=top_companies['metric_value'],
                    y=top_companies['company_name'],
                    orientation='h',
                    marker=dict(
                        color=top_companies['metric_value'],
                        colorscale='Viridis'
                    ),
                    text=top_companies['metric_value'].round(1),
                    textposition='auto',
                    hovertemplate="<b>%{y}</b><br>ROE: %{x:.2f}%<extra></extra>"
                )]
            )
            fig_bar.update_layout(
                title="Top 5 Companies by ROE",
                xaxis_title="ROE (%)",
                yaxis_title="",
                height=400,
                showlegend=False,
                margin=dict(l=150)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.warning("No company data available")
    
    # Sector Metrics Table
    st.markdown("---")
    st.subheader("📋 Sector Metrics Summary")
    
    if not sector_data.empty:
        display_data = sector_data.copy()
        display_data.columns = ['Sector', 'Count', 'Avg ROE (%)', 'Avg P/E']
        display_data['Avg ROE (%)'] = display_data['Avg ROE (%)'].apply(lambda x: f"{x:.2f}" if x else "N/A")
        display_data['Avg P/E'] = display_data['Avg P/E'].apply(lambda x: f"{x:.2f}" if x else "N/A")
        
        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Count": st.column_config.NumberColumn(format="%d"),
            }
        )
    
    # Footer
    st.markdown("---")
    st.caption(f"Data as of FY {selected_year} | Last Updated: {selected_year}")


if __name__ == "__main__":
    app()
