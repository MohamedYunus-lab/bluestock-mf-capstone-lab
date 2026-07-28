"""
Company Profile Screen - Detailed Company Analysis
Day 23: Company search, KPI tiles, charts, pros/cons badges
"""

import streamlit as st
import plotly.graph_objects as go
import sys
import os
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from dashboard.utils.db import (
    load_all_companies, load_company_by_id, load_company_ratios,
    load_company_profitandloss, load_prosandcons, load_latest_stock_price,
    search_companies
)


def app():
    """Company Profile screen main function"""
    st.title("👤 Company Profile")
    
    # Company search with autocomplete
    all_companies = load_all_companies()
    company_names = all_companies['company_name'].tolist()
    
    search_col, reset_col = st.columns([4, 1])
    
    with search_col:
        selected_company = st.selectbox(
            "Search Company",
            company_names,
            key="profile_company_search",
            placeholder="Type to search..."
        )
    
    with reset_col:
        if st.button("Clear", key="profile_reset"):
            st.rerun()
    
    if not selected_company:
        st.info("📌 Select a company to view details")
        return
    
    # Get company ID
    company_row = all_companies[all_companies['company_name'] == selected_company].iloc[0]
    company_id = company_row['company_id']
    
    # Load company data
    company_info = load_company_by_id(company_id)
    if not company_info:
        st.error("Company not found")
        return
    
    # Company Card Header
    st.markdown(f"## {company_info['company_name']}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.caption("Sector")
        st.write(f"**{company_info.get('sector_name', 'N/A')}**")
    
    with col2:
        st.caption("BSE Code")
        st.write(f"**{company_info.get('bse_code', 'N/A')}**")
    
    with col3:
        st.caption("NSE Code")
        st.write(f"**{company_info.get('nse_code', 'N/A')}**")
    
    with col4:
        st.caption("Market Cap (Cr)")
        mc = company_info.get('market_cap_inr')
        st.write(f"**₹{mc:,.0f}**" if mc else "**N/A**")
    
    # Load latest stock price
    stock_price = load_latest_stock_price(company_id)
    if stock_price:
        st.caption(f"Latest Price: ₹{stock_price.get('close_price', 'N/A')} | {stock_price.get('date', 'N/A')}")
    
    st.markdown("---")
    
    # KPI Tiles
    st.subheader("📊 Key Metrics")
    
    ratios = load_company_ratios(company_id, years=1)
    
    if not ratios.empty:
        latest_ratios = ratios.iloc[-1]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            roe = latest_ratios.get('roe')
            st.metric(
                "ROE (%)",
                f"{roe:.2f}" if roe else "N/A",
                delta="Return on Equity"
            )
        
        with col2:
            roce = latest_ratios.get('roce')
            st.metric(
                "ROCE (%)",
                f"{roce:.2f}" if roce else "N/A",
                delta="Return on Capital"
            )
        
        with col3:
            opm = latest_ratios.get('opm')
            st.metric(
                "OPM (%)",
                f"{opm:.2f}" if opm else "N/A",
                delta="Operating Margin"
            )
        
        col4, col5, col6 = st.columns(3)
        
        with col4:
            de = latest_ratios.get('debt_to_equity')
            st.metric(
                "D/E Ratio",
                f"{de:.2f}" if de else "N/A",
                delta="Leverage"
            )
        
        with col5:
            pe = latest_ratios.get('pe_ratio')
            st.metric(
                "P/E Ratio",
                f"{pe:.2f}" if pe else "N/A",
                delta="Valuation"
            )
        
        with col6:
            div_yield = latest_ratios.get('dividend_yield')
            st.metric(
                "Dividend Yield (%)",
                f"{div_yield:.2f}" if div_yield else "N/A",
                delta="Income"
            )
    
    st.markdown("---")
    
    # Revenue & Net Profit Chart (10-year)
    st.subheader("💹 Revenue & Net Profit Trend")
    
    pl_data = load_company_profitandloss(company_id, years=10)
    
    if not pl_data.empty:
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=pl_data['year'],
            y=pl_data['revenue_cr'],
            name='Revenue (Cr)',
            marker_color='lightblue',
            yaxis='y1'
        ))
        
        fig.add_trace(go.Scatter(
            x=pl_data['year'],
            y=pl_data['net_profit_cr'],
            name='Net Profit (Cr)',
            mode='lines+markers',
            line=dict(color='darkblue', width=2),
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="",
            xaxis_title="Year",
            yaxis_title="Revenue (Cr)",
            yaxis2=dict(
                title="Net Profit (Cr)",
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No P&L data available")
    
    # ROE/ROCE Dual-Axis Chart
    st.subheader("📈 ROE & ROCE Trend")
    
    if not ratios.empty:
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=ratios['year'],
            y=ratios['roe'],
            name='ROE (%)',
            mode='lines+markers',
            line=dict(color='#1f77b4', width=2),
            marker=dict(size=8)
        ))
        
        fig.add_trace(go.Scatter(
            x=ratios['year'],
            y=ratios['roce'],
            name='ROCE (%)',
            mode='lines+markers',
            line=dict(color='#ff7f0e', width=2),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="",
            xaxis_title="Year",
            yaxis_title="Return (%)",
            hovermode='x unified',
            height=400,
            legend=dict(x=0, y=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Pros and Cons
    st.markdown("---")
    st.subheader("✅ Strengths & Concerns")
    
    latest_year = ratios['year'].max() if not ratios.empty else 2023
    proscons = load_prosandcons(company_id, int(latest_year))
    
    if proscons:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Pros:**")
            if proscons.get('pros'):
                for pro in str(proscons.get('pros', '')).split(';'):
                    if pro.strip():
                        st.write(f"✅ {pro.strip()}")
            else:
                st.info("No data")
        
        with col2:
            st.markdown("**Cons:**")
            if proscons.get('cons'):
                for con in str(proscons.get('cons', '')).split(';'):
                    if con.strip():
                        st.write(f"⚠️ {con.strip()}")
            else:
                st.info("No data")
    else:
        st.info("No pros/cons data available")
    
    st.markdown("---")
    st.caption(f"Profile loaded in < 3 seconds | Data FY{int(latest_year)}")


if __name__ == "__main__":
    app()
