DASHBOARD DEVELOPMENT - HOW TO DO IT
=====================================

TASK: Create Power BI Dashboard
DUE: 30 Jun 2026
TIME: 7-8 hours

STEP-BY-STEP PROCESS
--------------------

STEP 1: Install Power BI Desktop (15 minutes)
----------------------------------------------
1. Go to: https://www.microsoft.com/en-us/power-platform/products/power-bi/desktop
2. Download Power BI Desktop (free)
3. Install and open

STEP 2: Validate Your Data (5 minutes)
---------------------------------------
Run this command in terminal:
   python dashboard\validate_data.py

You should see:
   ✓ All 10 CSV files found
   ✓ SQLite database with 22 tables
   ✓ Key metrics calculated

STEP 3: Import Data to Power BI (30 minutes)
---------------------------------------------
OPTION A: CSV Import (RECOMMENDED - EASIER)

1. Open Power BI Desktop
2. Click "Get Data" button
3. Select "Text/CSV"
4. Navigate to: C:\bluestock-mf-capstone\data\processed\
5. Select and import these files ONE BY ONE:
   - 01_fund_master_clean.csv
   - 02_nav_history_clean.csv
   - 03_aum_by_fund_house_clean.csv
   - 04_monthly_sip_inflows_clean.csv
   - 05_category_inflows_clean.csv
   - 06_industry_folio_count_clean.csv
   - 07_scheme_performance_clean.csv
   - 08_investor_transactions_clean.csv
   - 09_portfolio_holdings_clean.csv
   - 10_benchmark_indices_clean.csv

6. Click "Load" for each file
7. Wait for all data to load


OPTION B: SQLite Import (ADVANCED - IF YOU KNOW HOW)

1. Download SQLite ODBC driver: http://www.ch-werner.de/sqliteodbc/
2. Install the driver
3. In Power BI: Get Data > ODBC
4. Use database: C:\bluestock-mf-capstone\bluestock_mf.db

RECOMMENDATION: Use Option A (CSV) - much easier!

STEP 4: Create Relationships (15 minutes)
------------------------------------------
1. Click "Model" icon on left sidebar (looks like 3 connected boxes)
2. Drag these fields to connect tables:
   
   fund_master[amfi_code] → nav_history[amfi_code]
   fund_master[amfi_code] → scheme_performance[amfi_code]
   fund_master[amfi_code] → investor_transactions[amfi_code]
   
3. All relationships should show "1" to "*" (one-to-many)

STEP 5: Build Dashboard Pages (5-6 hours)
------------------------------------------
Read the detailed instructions in: POWER_BI_GUIDE.txt

Quick Summary:
- Page 1: Industry Overview (4 KPI cards, 2 charts)
- Page 2: Fund Performance (scatter plot, table, line chart, 3 slicers)
- Page 3: Investor Analytics (4 charts, 3 slicers)
- Page 4: SIP & Market Trends (3 charts)

For each page:
1. Click "+" at bottom to add new page
2. Rename the page
3. Drag visuals from Visualizations pane
4. Drag fields from Fields pane
5. Format using Format pane

STEP 6: Apply Theme and Branding (30 minutes)
----------------------------------------------
1. View tab > Themes > Select a professional theme
2. Use these colors:
   - Primary: #003366 (Dark Blue)
   - Accent: #FF9900 (Orange)
3. Make all titles 14pt Bold
4. Add subtle background color

STEP 7: Export Deliverables (30 minutes)
-----------------------------------------
1. Save PBIX:
   File > Save As > "bluestock_mf_dashboard.pbix"
   Save to: C:\bluestock-mf-capstone\dashboard\

2. Export PDF:
   File > Export > Export to PDF
   Save as: "Dashboard.pdf"

3. Export PNG Screenshots (for each page):
   - Go to page
   - File > Export > Export to Image
   - Save as:
     * Page1_Industry_Overview.png
     * Page2_Fund_Performance.png
     * Page3_Investor_Analytics.png
     * Page4_SIP_Market_Trends.png


WHAT TO SUBMIT
---------------

GITHUB (dashboard folder):
- validate_data.py (already there)
- POWER_BI_GUIDE.txt (already there)
- README.txt (this file)
- bluestock_mf_dashboard.pbix (you will create)

GOOGLE DRIVE (PPT/Slides or Dashboard folder):
- Dashboard.pdf
- Page1_Industry_Overview.png
- Page2_Fund_Performance.png
- Page3_Investor_Analytics.png
- Page4_SIP_Market_Trends.png


IMPORTANT TIPS
--------------
1. Save your work frequently (Ctrl+S)
2. If a visual doesn't look right, delete and recreate it
3. Use Top N filter to avoid showing too much data
4. Test all slicers - they should filter other visuals
5. Keep visuals clean and simple
6. Use consistent colors across all pages
7. Don't add too many visuals per page - it gets cluttered


HELP RESOURCES
--------------
If you get stuck:
1. Check POWER_BI_GUIDE.txt for detailed instructions
2. Check QUICK_REFERENCE.txt for key metrics and colors
3. YouTube: Search "Power BI tutorial for beginners"
4. Microsoft Learn: docs.microsoft.com/power-bi


TIME BREAKDOWN
--------------
Install Power BI: 15 min
Validate data: 5 min
Import data: 30 min
Create relationships: 15 min
Page 1: 60 min
Page 2: 90 min
Page 3: 90 min
Page 4: 90 min
Theme and polish: 30 min
Export: 30 min
TOTAL: ~7.5 hours


TROUBLESHOOTING
---------------
Problem: Can't find Power BI Desktop
Solution: Search "Power BI" in Windows Start menu

Problem: CSV files not loading
Solution: Check file path is correct, files should be in data/processed folder

Problem: Relationships not working
Solution: Make sure amfi_code is Text type, not Number

Problem: Charts showing wrong data
Solution: Check you dragged correct field to correct axis

Problem: PBIX file too large for GitHub
Solution: Keep PBIX in dashboard folder, add to .gitignore if needed


NEXT STEPS AFTER DASHBOARD
---------------------------
1. Take screenshots or record video demo
2. Prepare daily standups (see below)
3. Write note to admin for submission
4. Upload to GitHub and Google Drive


START NOW!
----------
1. Run: python dashboard\validate_data.py
2. Open Power BI Desktop
3. Follow POWER_BI_GUIDE.txt step by step
4. Take breaks every hour
5. You've got this!
