"""
Annual Reports Screen - Document Repository
Day 25: Company search, BSE PDF links by year
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from dashboard.utils.db import (
    load_all_companies, load_annual_report_links, load_company_by_id
)


def app():
    """Annual Reports screen main function"""
    st.title("📄 Annual Reports & Documents")
    
    # Company search
    all_companies = load_all_companies()
    company_names = all_companies['company_name'].tolist()
    
    selected_company = st.selectbox(
        "Select Company",
        company_names,
        key="reports_company_search",
        placeholder="Choose a company..."
    )
    
    if not selected_company:
        st.info("📌 Select a company to view annual reports")
        return
    
    # Get company ID and info
    company_row = all_companies[all_companies['company_name'] == selected_company].iloc[0]
    company_id = company_row['company_id']
    company_info = load_company_by_id(company_id)
    
    # Display company header
    st.subheader(f"{selected_company}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption("Sector")
        st.write(f"**{company_info.get('sector_name', 'N/A')}**")
    
    with col2:
        st.caption("BSE Code")
        st.write(f"**{company_info.get('bse_code', 'N/A')}**")
    
    with col3:
        st.caption("NSE Code")
        st.write(f"**{company_info.get('nse_code', 'N/A')}**")
    
    st.markdown("---")
    
    # Load annual reports
    reports = load_annual_report_links(company_id)
    
    if reports.empty:
        st.warning("No annual report links available in database")
        
        st.info("""
        📌 **To add annual report links:**
        1. Update the `documents` table in the database with:
           - `company_id`: Company identifier
           - `year`: Fiscal year
           - `doc_type`: 'Annual_Report'
           - `doc_url`: BSE/NSE filing URL
           - `filing_date`: Filing date
        
        2. Example BSE URL pattern:
           `https://www.bseindia.com/corporates/<bse_code>/<filing_id>.pdf`
        """)
        
        return
    
    st.subheader(f"📋 Available Reports ({len(reports)} years)")
    
    # Display reports
    for _, report in reports.sort_values('year', ascending=False).iterrows():
        year = report['year']
        url = report['doc_url']
        filing_date = report['filing_date']
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.write(f"**FY {int(year)}**")
        
        with col2:
            if filing_date:
                st.caption(f"Filed: {filing_date}")
            else:
                st.caption("Date not available")
        
        with col3:
            if url:
                st.markdown(f"[📥 Download]({url})")
            else:
                st.caption("Link not available")
    
    st.markdown("---")
    
    # Document type summary
    st.subheader("📊 Document Coverage")
    
    if not reports.empty:
        year_range = f"{int(reports['year'].min())} - {int(reports['year'].max())}"
        st.write(f"**Years Covered:** {year_range}")
        st.write(f"**Total Reports:** {len(reports)}")
        
        # Display as table
        display_data = reports[['year', 'filing_date', 'doc_url']].copy()
        display_data.columns = ['Year', 'Filing Date', 'Document Link']
        display_data = display_data.sort_values('Year', ascending=False)
        
        # Format for display
        display_data['Year'] = display_data['Year'].astype(int)
        display_data['Filing Date'] = display_data['Filing Date'].fillna('N/A')
        display_data['Document Link'] = display_data['Document Link'].apply(
            lambda x: f"[View]({x})" if x else "N/A"
        )
        
        st.markdown(display_data.to_markdown(index=False))
    
    st.markdown("---")
    
    # Additional resources
    st.subheader("🔗 Additional Resources")
    
    bse_code = company_info.get('bse_code', '')
    nse_code = company_info.get('nse_code', '')
    
    col1, col2 = st.columns(2)
    
    with col1:
        if bse_code:
            st.markdown(f"""
            **BSE Resources:**
            - [BSE Announcements](https://www.bseindia.com/corporates/{bse_code})
            - [BSE Corporate Filings](https://www.bseindia.com/corporates/)
            """)
    
    with col2:
        if nse_code:
            st.markdown(f"""
            **NSE Resources:**
            - [NSE Company Page](https://www.nseindia.com)
            - [NSE Corporate Actions](https://www.nseindia.com)
            """)
    
    st.markdown("---")
    
    # Instructions for sourcing documents
    with st.expander("📖 How to Find Annual Reports"):
        st.markdown("""
        ### BSE (Bombay Stock Exchange)
        1. Visit: https://www.bseindia.com
        2. Go to **Corporate Info > Announcements**
        3. Search by BSE code and select company
        4. Filter by document type: **Annual Report**
        5. Download and extract PDF URL
        
        ### NSE (National Stock Exchange)
        1. Visit: https://www.nseindia.com
        2. Go to **Market Data > Corporate Actions**
        3. Search by NSE symbol
        4. Look for **Annual Report** filings
        
        ### Alternative Sources
        - Company website investor relations section
        - MCA (Ministry of Corporate Affairs) filing portal
        - SEBI filings database
        """)


if __name__ == "__main__":
    app()
