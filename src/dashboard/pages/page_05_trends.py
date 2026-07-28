"""
Trend Analysis Screen - Multi-Year Metric Trends
Day 25: Company search, 3-metric selector, 10-year line chart with YoY %
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from dashboard.utils.db import (
    load_all_companies, load_company_ratios, search_companies, get_available_years
)


def calculate_yoy_change(series):
    """Calculate year-over-year percentage change"""
    return series.pct_change() * 100


def app():
    """Trend Analysis screen main function"""
    st.title("📈 Trend Analysis")
    
    # Company search
    all_companies = load_all_companies()
    company_names = all_companies['company_name'].tolist()
    
    selected_company = st.selectbox(
        "Select Company",
        company_names,
        key="trend_company_search",
        placeholder="Choose a company..."
    )
    
    if not selected_company:
        st.info("📌 Select a company to view trends")
        return
    
    # Get company ID
    company_row = all_companies[all_companies['company_name'] == selected_company].iloc[0]
    company_id = company_row['company_id']
    
    # Load 10-year data
    ratios = load_company_ratios(company_id, years=10)
    
    if ratios.empty:
        st.warning("No trend data available for this company")
        return
    
    st.markdown("---")
    st.subheader("🎯 Metric Selection")
    
    # Metric selector - choose 3 metrics
    available_metrics = [
        'ROE (%)', 'ROCE (%)', 'OPM (%)', 'NPM (%)',
        'D/E Ratio', 'P/E Ratio', 'P/B Ratio',
        'Dividend Yield (%)', 'Asset Turnover'
    ]
    
    metric_mapping = {
        'ROE (%)': 'roe',
        'ROCE (%)': 'roce',
        'OPM (%)': 'opm',
        'NPM (%)': 'npm',
        'D/E Ratio': 'debt_to_equity',
        'P/E Ratio': 'pe_ratio',
        'P/B Ratio': 'pb_ratio',
        'Dividend Yield (%)': 'dividend_yield',
        'Asset Turnover': 'asset_turnover'
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        metric1 = st.selectbox("Metric 1", available_metrics, index=0, key="trend_metric1")
    
    with col2:
        metric2 = st.selectbox("Metric 2", available_metrics, index=3, key="trend_metric2")
    
    with col3:
        metric3 = st.selectbox("Metric 3", available_metrics, index=5, key="trend_metric3")
    
    st.markdown("---")
    
    # Create multi-metric chart
    st.subheader(f"📊 {selected_company} - 10-Year Trends")
    
    fig = go.Figure()
    
    # Get metric column names
    metric1_col = metric_mapping[metric1]
    metric2_col = metric_mapping[metric2]
    metric3_col = metric_mapping[metric3]
    
    # Add traces
    if metric1_col in ratios.columns:
        fig.add_trace(go.Scatter(
            x=ratios['year'],
            y=ratios[metric1_col],
            mode='lines+markers',
            name=metric1,
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=8),
            yaxis='y1'
        ))
    
    if metric2_col in ratios.columns:
        fig.add_trace(go.Scatter(
            x=ratios['year'],
            y=ratios[metric2_col],
            mode='lines+markers',
            name=metric2,
            line=dict(color='#ff7f0e', width=2),
            marker=dict(size=8),
            yaxis='y2'
        ))
    
    if metric3_col in ratios.columns:
        fig.add_trace(go.Scatter(
            x=ratios['year'],
            y=ratios[metric3_col],
            mode='lines+markers',
            name=metric3,
            line=dict(color='#2ca02c', width=2),
            marker=dict(size=8),
            yaxis='y3'
        ))
    
    # Update layout with multiple Y axes
    fig.update_layout(
        title="",
        xaxis_title="Year",
        yaxis_title=metric1,
        yaxis2=dict(
            title=metric2,
            overlaying='y',
            side='right',
            anchor='x'
        ),
        yaxis3=dict(
            title=metric3,
            overlaying='y',
            side='left',
            anchor='free',
            position=0.0 if metric3_col == metric1_col else 0.15
        ),
        hovermode='x unified',
        height=500,
        legend=dict(x=0, y=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # YoY Change Table
    st.subheader("📊 Year-over-Year Change (%)")
    
    yoy_data = ratios[['year', metric1_col, metric2_col, metric3_col]].copy()
    yoy_data.columns = ['Year', metric1, metric2, metric3]
    
    # Calculate YoY changes
    for col in [metric1, metric2, metric3]:
        yoy_data[f'{col} YoY %'] = yoy_data[col].pct_change() * 100
    
    display_cols = ['Year', metric1, f'{metric1} YoY %', metric2, f'{metric2} YoY %', metric3, f'{metric3} YoY %']
    display_data = yoy_data[display_cols].copy()
    
    # Format numeric columns
    for col in display_data.columns:
        if col != 'Year':
            display_data[col] = display_data[col].apply(lambda x: f"{x:.2f}" if x else "N/A")
    
    st.dataframe(display_data, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Summary stats
    st.subheader("📈 Trend Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        latest_m1 = ratios[metric1_col].iloc[-1] if not ratios.empty else 0
        oldest_m1 = ratios[metric1_col].iloc[0] if not ratios.empty else 0
        change_m1 = ((latest_m1 - oldest_m1) / abs(oldest_m1)) * 100 if oldest_m1 != 0 else 0
        st.metric(
            f"{metric1} (Latest vs 10-yr ago)",
            f"{latest_m1:.2f}",
            delta=f"{change_m1:+.1f}%"
        )
    
    with col2:
        latest_m2 = ratios[metric2_col].iloc[-1] if not ratios.empty else 0
        oldest_m2 = ratios[metric2_col].iloc[0] if not ratios.empty else 0
        change_m2 = ((latest_m2 - oldest_m2) / abs(oldest_m2)) * 100 if oldest_m2 != 0 else 0
        st.metric(
            f"{metric2} (Latest vs 10-yr ago)",
            f"{latest_m2:.2f}",
            delta=f"{change_m2:+.1f}%"
        )
    
    with col3:
        latest_m3 = ratios[metric3_col].iloc[-1] if not ratios.empty else 0
        oldest_m3 = ratios[metric3_col].iloc[0] if not ratios.empty else 0
        change_m3 = ((latest_m3 - oldest_m3) / abs(oldest_m3)) * 100 if oldest_m3 != 0 else 0
        st.metric(
            f"{metric3} (Latest vs 10-yr ago)",
            f"{latest_m3:.2f}",
            delta=f"{change_m3:+.1f}%"
        )


if __name__ == "__main__":
    app()
