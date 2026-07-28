"""
Capital Allocation Screen - Portfolio Strategy Visualization
Day 25: Treemap of 92 companies by 8 allocation patterns
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
    load_all_companies, get_available_years
)


def classify_capital_allocation(company_id: str, year: int) -> dict:
    """Classify company capital allocation pattern"""
    DB_PATH = 'c:/bluestock-mf-capstone/n100/db/nifty100.db'
    conn = sqlite3.connect(DB_PATH)
    
    query = """
    SELECT 
        pl.net_profit_cr,
        cf.operating_cf_cr,
        cf.investing_cf_cr,
        cf.financing_cf_cr,
        cf.free_cash_flow_cr
    FROM profitandloss pl
    JOIN cashflow cf ON pl.company_id = cf.company_id AND pl.year = cf.year
    WHERE pl.company_id = ? AND pl.year = ?
    """
    
    cursor = conn.execute(query, (company_id, year))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {'pattern': 'Unknown', 'confidence': 0}
    
    net_profit = row[0] or 0
    ocf = row[1] or 0
    icf = row[2] or 0
    fcf = row[3] or 0
    fcf_direct = row[4] or 0
    
    # Classification logic
    if net_profit <= 0:
        return {'pattern': 'Turnaround', 'confidence': 0.7}
    
    # Calculate ratios
    reinvestment_ratio = icf / ocf if ocf != 0 else 0
    leverage_change = fcf / net_profit if net_profit != 0 else 0
    
    if reinvestment_ratio > 0.8:
        return {'pattern': 'Reinvestment', 'confidence': 0.85}
    elif leverage_change < -0.3:
        return {'pattern': 'Deleveraging', 'confidence': 0.80}
    elif leverage_change > 0.3:
        return {'pattern': 'Debt Accumulation', 'confidence': 0.75}
    elif reinvestment_ratio > 0.5 and leverage_change > -0.1:
        return {'pattern': 'Growth-Focused', 'confidence': 0.80}
    elif reinvestment_ratio < 0.3:
        return {'pattern': 'Shareholder Returns', 'confidence': 0.75}
    elif reinvestment_ratio < 0.5 and leverage_change > -0.1:
        return {'pattern': 'Balanced', 'confidence': 0.80}
    else:
        return {'pattern': 'Conservative', 'confidence': 0.70}


def app():
    """Capital Allocation screen main function"""
    st.title("💰 Capital Allocation Analysis")
    
    st.info("📌 Treemap showing how 92 Nifty 100 companies allocate capital across 8 patterns")
    
    # Year selector
    available_years = get_available_years()
    selected_year = st.selectbox("Select Year", available_years, index=0, key="allocation_year")
    
    # Load all companies
    all_companies = load_all_companies()
    
    # Classify each company
    allocation_data = []
    
    for _, company in all_companies.iterrows():
        company_id = company['company_id']
        company_name = company['company_name']
        sector = company['sector_name']
        
        classification = classify_capital_allocation(company_id, int(selected_year))
        
        allocation_data.append({
            'company_id': company_id,
            'company_name': company_name,
            'sector': sector,
            'pattern': classification['pattern'],
            'confidence': classification['confidence'],
            'size': 1  # For counting
        })
    
    df_allocation = pd.DataFrame(allocation_data)
    
    # Create treemap data
    treemap_data = df_allocation.groupby('pattern').agg({
        'company_name': 'count',
        'confidence': 'mean'
    }).reset_index()
    treemap_data.columns = ['pattern', 'count', 'avg_confidence']
    
    # Color mapping for patterns
    pattern_colors = {
        'Reinvestment': '#1f77b4',
        'Shareholder Returns': '#ff7f0e',
        'Deleveraging': '#2ca02c',
        'Debt Accumulation': '#d62728',
        'Growth-Focused': '#9467bd',
        'Conservative': '#8c564b',
        'Balanced': '#e377c2',
        'Turnaround': '#7f7f7f'
    }
    
    # Create treemap
    fig = px.treemap(
        df_allocation,
        labels='company_name',
        parents='pattern',
        values='confidence',
        color='pattern',
        color_discrete_map=pattern_colors,
        title="",
        hover_data={'company_name': True, 'sector': True, 'pattern': True}
    )
    
    fig.update_layout(
        height=600,
        font=dict(size=10)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Pattern Summary
    st.subheader("📊 Capital Allocation Pattern Distribution")
    
    pattern_summary = []
    for _, row in treemap_data.iterrows():
        pattern_summary.append({
            'Pattern': row['pattern'],
            'Companies': int(row['count']),
            'Avg Confidence': f"{row['avg_confidence']:.2%}",
            'Examples': ', '.join(
                df_allocation[df_allocation['pattern'] == row['pattern']]['company_name'].head(3).tolist()
            )
        })
    
    df_summary = pd.DataFrame(pattern_summary)
    st.dataframe(df_summary, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Pattern Definitions
    st.subheader("📖 Pattern Definitions")
    
    patterns_def = {
        '🏭 Reinvestment': 'Companies reinvesting heavily in growth and capex (CapEx/OCF > 80%)',
        '💵 Shareholder Returns': 'Companies returning capital through dividends and buybacks (CapEx/OCF < 30%)',
        '📉 Deleveraging': 'Companies actively reducing debt burden (FCF/NP < -0.3)',
        '📈 Debt Accumulation': 'Companies taking on debt for growth (FCF/NP > 0.3)',
        '🚀 Growth-Focused': 'Balanced reinvestment with moderate leverage increase',
        '🛡️ Conservative': 'Defensive allocation with low capex and stable debt',
        '⚖️ Balanced': 'Balanced approach between reinvestment and returns',
        '⚠️ Turnaround': 'Companies with negative or near-zero profits (Recovery phase)',
    }
    
    with st.expander("View Pattern Definitions"):
        for pattern, definition in patterns_def.items():
            st.write(f"**{pattern}**: {definition}")
    
    st.markdown("---")
    
    # Company Details
    st.subheader("🔍 Company-Level Details")
    
    selected_pattern = st.selectbox(
        "Filter by Pattern",
        ['All'] + sorted(df_allocation['pattern'].unique().tolist()),
        key="allocation_pattern_filter"
    )
    
    if selected_pattern == 'All':
        display_df = df_allocation
    else:
        display_df = df_allocation[df_allocation['pattern'] == selected_pattern]
    
    display_cols = display_df[['company_name', 'sector', 'pattern', 'confidence']].copy()
    display_cols.columns = ['Company', 'Sector', 'Pattern', 'Confidence']
    display_cols = display_cols.sort_values('Confidence', ascending=False)
    
    st.dataframe(display_cols, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.caption(f"Analysis for FY {selected_year} | {len(df_allocation)} companies classified")


if __name__ == "__main__":
    app()
