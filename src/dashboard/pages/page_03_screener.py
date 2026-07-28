"""
Screener Screen - Multi-Factor Stock Screener
Day 24: 10 metric sliders, 6 preset buttons, live updates, CSV download
"""

import streamlit as st
import pandas as pd
import sys
import os
import csv
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from dashboard.utils.db import (
    get_available_years, load_all_companies
)


def get_screened_companies(
    roe_min: float, roe_max: float,
    de_min: float, de_max: float,
    fcf_min: float, fcf_max: float,
    revenue_cagr_min: float, revenue_cagr_max: float,
    pat_cagr_min: float, pat_cagr_max: float,
    opm_min: float, opm_max: float,
    pe_min: float, pe_max: float,
    pb_min: float, pb_max: float,
    div_yield_min: float, div_yield_max: float,
    icr_min: float, icr_max: float,
    year: int = 2023
) -> pd.DataFrame:
    """Screen companies based on multiple criteria"""
    import sqlite3
    
    DB_PATH = 'c:/bluestock-mf-capstone/n100/db/nifty100.db'
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    query = """
    SELECT 
        c.company_id,
        c.company_name,
        s.sector_name,
        fr.roe,
        fr.debt_to_equity,
        fr.fcf,
        fr.opm,
        fr.pe_ratio,
        fr.pb_ratio,
        fr.dividend_yield,
        fr.icr
    FROM companies c
    LEFT JOIN sectors s ON c.sector_id = s.sector_id
    LEFT JOIN financial_ratios fr ON c.company_id = fr.company_id AND fr.year = ?
    WHERE 1=1
    """
    
    params = [year]
    
    if roe_min is not None:
        query += " AND fr.roe >= ?"
        params.append(roe_min)
    if roe_max is not None:
        query += " AND fr.roe <= ?"
        params.append(roe_max)
    
    if de_min is not None:
        query += " AND fr.debt_to_equity >= ?"
        params.append(de_min)
    if de_max is not None:
        query += " AND fr.debt_to_equity <= ?"
        params.append(de_max)
    
    if fcf_min is not None:
        query += " AND fr.fcf >= ?"
        params.append(fcf_min)
    if fcf_max is not None:
        query += " AND fr.fcf <= ?"
        params.append(fcf_max)
    
    if opm_min is not None:
        query += " AND fr.opm >= ?"
        params.append(opm_min)
    if opm_max is not None:
        query += " AND fr.opm <= ?"
        params.append(opm_max)
    
    if pe_min is not None:
        query += " AND fr.pe_ratio >= ?"
        params.append(pe_min)
    if pe_max is not None:
        query += " AND fr.pe_ratio <= ?"
        params.append(pe_max)
    
    if pb_min is not None:
        query += " AND fr.pb_ratio >= ?"
        params.append(pb_min)
    if pb_max is not None:
        query += " AND fr.pb_ratio <= ?"
        params.append(pb_max)
    
    if div_yield_min is not None:
        query += " AND fr.dividend_yield >= ?"
        params.append(div_yield_min)
    if div_yield_max is not None:
        query += " AND fr.dividend_yield <= ?"
        params.append(div_yield_max)
    
    if icr_min is not None:
        query += " AND fr.icr >= ?"
        params.append(icr_min)
    if icr_max is not None:
        query += " AND fr.icr <= ?"
        params.append(icr_max)
    
    query += " ORDER BY c.company_name"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df


def app():
    """Screener screen main function"""
    st.title("🔍 Stock Screener")
    
    # Year selector
    available_years = get_available_years()
    selected_year = st.selectbox("Select Year", available_years, index=0, key="screener_year")
    
    st.markdown("---")
    
    # Preset filter buttons
    st.subheader("⚡ Preset Filters")
    
    preset_col1, preset_col2, preset_col3 = st.columns(3)
    preset_col4, preset_col5, preset_col6 = st.columns(3)
    
    with preset_col1:
        if st.button("🏆 Quality", key="preset_quality"):
            st.session_state.preset = "quality"
    
    with preset_col2:
        if st.button("💎 Value", key="preset_value"):
            st.session_state.preset = "value"
    
    with preset_col3:
        if st.button("🚀 Growth", key="preset_growth"):
            st.session_state.preset = "growth"
    
    with preset_col4:
        if st.button("💰 Dividend", key="preset_dividend"):
            st.session_state.preset = "dividend"
    
    with preset_col5:
        if st.button("🛡️ Debt-Free", key="preset_debtfree"):
            st.session_state.preset = "debt_free"
    
    with preset_col6:
        if st.button("📈 Turnaround", key="preset_turnaround"):
            st.session_state.preset = "turnaround"
    
    st.markdown("---")
    st.subheader("🎚️ Custom Filters")
    
    # Initialize session state for filters
    if "preset" not in st.session_state:
        st.session_state.preset = None
    
    # Apply presets
    if st.session_state.preset == "quality":
        st.info("Quality Filter: ROE > 15%, D/E < 1.0, OPM > 15%")
        roe_range = (15.0, 100.0)
        de_range = (0.0, 1.0)
        opm_range = (15.0, 100.0)
        pe_range = (0.0, 30.0)
    elif st.session_state.preset == "value":
        st.info("Value Filter: P/E < 15, P/B < 2.0")
        pe_range = (0.0, 15.0)
        pb_range = (0.0, 2.0)
        roe_range = (0.0, 100.0)
        de_range = (0.0, 5.0)
        opm_range = (0.0, 100.0)
    elif st.session_state.preset == "growth":
        st.info("Growth Filter: Revenue CAGR > 15%, PAT CAGR > 15%, P/E < 25")
        roe_range = (10.0, 100.0)
        de_range = (0.0, 2.0)
        pe_range = (0.0, 25.0)
        opm_range = (0.0, 100.0)
        pb_range = (0.0, 100.0)
    elif st.session_state.preset == "dividend":
        st.info("Dividend Filter: Dividend Yield > 2%, D/E < 1.5")
        de_range = (0.0, 1.5)
        roe_range = (0.0, 100.0)
        opm_range = (0.0, 100.0)
        pe_range = (0.0, 100.0)
        pb_range = (0.0, 100.0)
    elif st.session_state.preset == "debt_free":
        st.info("Debt-Free Filter: D/E = 0, ROE > 10%")
        de_range = (0.0, 0.1)
        roe_range = (10.0, 100.0)
        opm_range = (0.0, 100.0)
        pe_range = (0.0, 100.0)
        pb_range = (0.0, 100.0)
    else:
        roe_range = (0.0, 100.0)
        de_range = (0.0, 5.0)
        opm_range = (0.0, 100.0)
        pe_range = (0.0, 100.0)
        pb_range = (0.0, 100.0)
    
    # Metric sliders
    col1, col2, col3 = st.columns(3)
    
    with col1:
        roe_range = st.slider("ROE (%)", 0.0, 100.0, roe_range, key="slider_roe")
        de_range = st.slider("D/E Ratio", 0.0, 5.0, de_range, key="slider_de")
        opm_range = st.slider("OPM (%)", 0.0, 100.0, opm_range, key="slider_opm")
        fcf_range = st.slider("FCF (Cr)", -1000.0, 10000.0, (-1000.0, 10000.0), key="slider_fcf")
    
    with col2:
        pe_range = st.slider("P/E Ratio", 0.0, 100.0, pe_range, key="slider_pe")
        pb_range = st.slider("P/B Ratio", 0.0, 100.0, pb_range, key="slider_pb")
        div_range = st.slider("Dividend Yield (%)", 0.0, 20.0, (0.0, 20.0), key="slider_div")
        icr_range = st.slider("ICR", 0.0, 50.0, (0.0, 50.0), key="slider_icr")
    
    with col3:
        rev_cagr_range = st.slider("Revenue CAGR (%)", -50.0, 100.0, (-50.0, 100.0), key="slider_rev_cagr")
        pat_cagr_range = st.slider("PAT CAGR (%)", -50.0, 100.0, (-50.0, 100.0), key="slider_pat_cagr")
    
    st.markdown("---")
    
    # Screen button
    if st.button("🔎 Apply Filters", key="screen_apply", type="primary"):
        
        results = get_screened_companies(
            roe_min=roe_range[0], roe_max=roe_range[1],
            de_min=de_range[0], de_max=de_range[1],
            fcf_min=fcf_range[0], fcf_max=fcf_range[1],
            revenue_cagr_min=rev_cagr_range[0], revenue_cagr_max=rev_cagr_range[1],
            pat_cagr_min=pat_cagr_range[0], pat_cagr_max=pat_cagr_range[1],
            opm_min=opm_range[0], opm_max=opm_range[1],
            pe_min=pe_range[0], pe_max=pe_range[1],
            pb_min=pb_range[0], pb_max=pb_range[1],
            div_yield_min=div_range[0], div_yield_max=div_range[1],
            icr_min=icr_range[0], icr_max=icr_range[1],
            year=int(selected_year)
        )
        
        st.session_state.screener_results = results
    
    # Display results
    if "screener_results" in st.session_state:
        results = st.session_state.screener_results
        
        st.subheader(f"📊 Results ({len(results)} companies)")
        
        if len(results) > 0:
            # Display table
            display_cols = ['company_name', 'sector_name', 'roe', 'debt_to_equity', 'pe_ratio', 'dividend_yield']
            display_data = results[display_cols].copy()
            display_data.columns = ['Company', 'Sector', 'ROE (%)', 'D/E', 'P/E', 'Div Yield (%)']
            
            st.dataframe(display_data, use_container_width=True, hide_index=True)
            
            # Download CSV
            csv_buffer = results.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv_buffer,
                file_name=f"screener_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No companies match the selected criteria. Try adjusting the filters.")


if __name__ == "__main__":
    app()
