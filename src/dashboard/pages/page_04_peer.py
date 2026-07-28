"""
Peer Comparison Screen - Company vs Peer Benchmarking
Day 24: Peer group dropdown, radar chart, KPI table with benchmarks
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from dashboard.utils.db import (
    load_all_companies, load_company_by_id, load_company_ratios,
    load_peer_group, load_sector_medians, get_available_years
)


def app():
    """Peer Comparison screen main function"""
    st.title("📊 Peer Comparison")
    
    # Company selection
    all_companies = load_all_companies()
    company_names = all_companies['company_name'].tolist()
    
    selected_company = st.selectbox(
        "Select Company",
        company_names,
        key="peer_company_search",
        placeholder="Choose a company..."
    )
    
    if not selected_company:
        st.info("📌 Select a company to view peer comparison")
        return
    
    # Get company ID and info
    company_row = all_companies[all_companies['company_name'] == selected_company].iloc[0]
    company_id = company_row['company_id']
    company_info = load_company_by_id(company_id)
    
    # Year selector
    available_years = get_available_years()
    selected_year = st.selectbox("Select Year", available_years, index=0, key="peer_year")
    
    st.markdown("---")
    
    # Load peer group
    peers = load_peer_group(company_id)
    
    if peers.empty:
        st.warning("No peer group data available for this company")
        return
    
    st.subheader(f"🤝 Peers of {selected_company}")
    st.write(f"**Sector:** {company_info.get('sector_name', 'N/A')}")
    st.write(f"**Peer Count:** {len(peers)}")
    
    # Load ratios
    company_ratios = load_company_ratios(company_id, years=1)
    
    if company_ratios.empty:
        st.warning("No ratio data available")
        return
    
    company_latest = company_ratios.iloc[-1]
    
    # Calculate peer averages
    peer_ids = peers['company_id'].tolist()
    peer_ratios_list = []
    
    for peer_id in peer_ids:
        peer_ratio = load_company_ratios(peer_id, years=1)
        if not peer_ratio.empty:
            peer_ratios_list.append(peer_ratio.iloc[-1])
    
    if not peer_ratios_list:
        st.warning("No peer ratio data available")
        return
    
    peer_avg = pd.DataFrame(peer_ratios_list).mean()
    
    st.markdown("---")
    
    # Radar Chart Comparison
    st.subheader("📈 Radar Chart: Company vs Peer Average")
    
    metrics_for_radar = ['roe', 'roce', 'opm', 'debt_to_equity', 'pe_ratio']
    
    company_values = [company_latest.get(m, 0) for m in metrics_for_radar]
    peer_values = [peer_avg.get(m, 0) for m in metrics_for_radar]
    
    # Normalize for visualization
    max_values = {
        'roe': 40,
        'roce': 40,
        'opm': 30,
        'debt_to_equity': 2,
        'pe_ratio': 40
    }
    
    company_normalized = [
        (company_values[i] / max_values[metrics_for_radar[i]]) * 100 
        if max_values[metrics_for_radar[i]] != 0 else 0
        for i in range(len(metrics_for_radar))
    ]
    
    peer_normalized = [
        (peer_values[i] / max_values[metrics_for_radar[i]]) * 100 
        if max_values[metrics_for_radar[i]] != 0 else 0
        for i in range(len(metrics_for_radar))
    ]
    
    # Create radar chart
    fig = go.Figure(data=[
        go.Scatterpolar(
            r=company_normalized,
            theta=metrics_for_radar,
            fill='toself',
            name=selected_company,
            line=dict(color='#1f77b4')
        ),
        go.Scatterpolar(
            r=peer_normalized,
            theta=metrics_for_radar,
            fill='toself',
            name='Peer Average',
            line=dict(color='#ff7f0e')
        )
    ])
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # KPI Table with Benchmarks
    st.subheader("📋 Detailed KPI Comparison")
    
    kpi_data = {
        'Metric': ['ROE (%)', 'ROCE (%)', 'OPM (%)', 'NPM (%)', 'D/E Ratio', 'P/E Ratio', 'P/B Ratio', 'Dividend Yield (%)'],
        'Company': [
            f"{company_latest.get('roe', 0):.2f}",
            f"{company_latest.get('roce', 0):.2f}",
            f"{company_latest.get('opm', 0):.2f}",
            f"{company_latest.get('npm', 0):.2f}",
            f"{company_latest.get('debt_to_equity', 0):.2f}",
            f"{company_latest.get('pe_ratio', 0):.2f}",
            f"{company_latest.get('pb_ratio', 0):.2f}",
            f"{company_latest.get('dividend_yield', 0):.2f}",
        ],
        'Peer Avg': [
            f"{peer_avg.get('roe', 0):.2f}",
            f"{peer_avg.get('roce', 0):.2f}",
            f"{peer_avg.get('opm', 0):.2f}",
            f"{peer_avg.get('npm', 0):.2f}",
            f"{peer_avg.get('debt_to_equity', 0):.2f}",
            f"{peer_avg.get('pe_ratio', 0):.2f}",
            f"{peer_avg.get('pb_ratio', 0):.2f}",
            f"{peer_avg.get('dividend_yield', 0):.2f}",
        ],
        'vs Peer': [
            f"{((float(company_latest.get('roe', 0)) / float(peer_avg.get('roe', 1))) - 1) * 100:.1f}%",
            f"{((float(company_latest.get('roce', 0)) / float(peer_avg.get('roce', 1))) - 1) * 100:.1f}%",
            f"{((float(company_latest.get('opm', 0)) / float(peer_avg.get('opm', 1))) - 1) * 100:.1f}%",
            f"{((float(company_latest.get('npm', 0)) / float(peer_avg.get('npm', 1))) - 1) * 100:.1f}%",
            f"{((float(company_latest.get('debt_to_equity', 0)) / float(peer_avg.get('debt_to_equity', 1))) - 1) * 100:.1f}%",
            f"{((float(company_latest.get('pe_ratio', 0)) / float(peer_avg.get('pe_ratio', 1))) - 1) * 100:.1f}%",
            f"{((float(company_latest.get('pb_ratio', 0)) / float(peer_avg.get('pb_ratio', 1))) - 1) * 100:.1f}%",
            f"{((float(company_latest.get('dividend_yield', 0)) / float(peer_avg.get('dividend_yield', 1))) - 1) * 100:.1f}%",
        ]
    }
    
    df_kpi = pd.DataFrame(kpi_data)
    st.dataframe(df_kpi, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Peer List
    st.subheader("👥 Peer Group Members")
    
    peer_display = peers[['company_name', 'sector_name']].copy()
    peer_display.columns = ['Company', 'Sector']
    st.dataframe(peer_display, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    app()
