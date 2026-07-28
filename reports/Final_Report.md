BLUESTOCK MUTUAL FUNDS ANALYTICS CAPSTONE - FINAL REPORT
========================================================

EXECUTIVE SUMMARY
-----------------

This capstone project completed a comprehensive analytics platform for Indian mutual fund data covering 40 schemes, 32,778 investor transactions, and 3+ years of historical NAV data (2022-2026).

PROJECT SCOPE
-------------

Data Sources: 10 datasets from AMFI (Association of Mutual Funds in India)
Time Period: January 2022 - December 2025
Schemes Analyzed: 40 mutual funds across 10 categories
Investors Tracked: 32,778 transactions from diverse demographics
Database: SQLite with 22 normalized tables

DELIVERABLES COMPLETED
----------------------

1. ETL Pipeline
   - Automated data ingestion from CSV files
   - Live NAV fetching from mfapi.in API
   - Data validation and quality checks
   - SQLite database loading with transactions

2. Data Cleaning & Database Design
   - Standardized column naming (lowercase_underscore)
   - Date format normalization
   - Missing value handling
   - Star schema with dim_fund and 9 fact tables

3. Exploratory Data Analysis
   - 15 visualizations covering industry metrics
   - NAV trends showing 2023 bull run and 2024 corrections
   - AUM growth by fund house (SBI dominance at Rs 12.5L Cr)
   - SIP inflows peak of Rs 31,002 Cr (Dec 2025)
   - Geographic distribution (T30 cities 65.9%)
   - Investor demographics by age, gender, state

4. Performance Analytics
   - Daily returns computation for all 40 schemes
   - CAGR calculation (1yr, 3yr, 5yr periods)
   - Sharpe Ratio ranking (Mirae Asset Large Cap: 1.448)
   - Sortino Ratio using downside deviation
   - Alpha-Beta regression vs Nifty 100
   - Maximum drawdown analysis
   - Composite fund scorecard (0-100 weighted score)

5. Interactive Dashboard (Power BI)
   - Industry Overview: 4 KPI cards, AUM trends, fund house comparison
   - Fund Performance: Risk-return scatter, scorecard table, NAV charts, slicers
   - Investor Analytics: State distribution, demographics, continuity trends
   - SIP & Market Trends: Dual-axis SIP vs Nifty, category heatmap

6. Advanced Analytics
   - Value at Risk (VaR) at 95% confidence
   - Conditional VaR (CVaR) for tail risk
   - Rolling 90-day Sharpe ratio trends
   - Investor cohort analysis by transaction year
   - SIP continuity detection (at-risk flagging)
   - Risk-based fund recommender system
   - Sector concentration metrics (Herfindahl Index)

KEY FINDINGS
------------

Market Trends:
- Strong bull run in 2023 (+40% AUM growth)
- 2024 saw market corrections but SIP resilience
- SIP mode shows strong continuity (99.97% rate)
- T30 cities dominate with 65.9% of SIP inflows

Fund Performance:
- Top performer: Axis Midcap Fund (35.10% 3-yr CAGR)
- Best risk-adjusted: Mirae Asset Large Cap (1.448 Sharpe)
- Lowest risk: Liquid funds (near-zero volatility)
- Portfolio concentration varies (HHI 0.02-0.21)

Investor Behavior:
- 2024 cohort invested Rs 391.76 Lakh Cr (highest year)
- Average SIP amount: Rs 2,847 per transaction
- 2,950 investors with 6+ SIP transactions
- At-risk investors: 0.03% (extremely low churn)

Recommendations:
- Low risk: ICICI Liquid Fund, SBI Gilt Fund
- Moderate: Balanced & multi-asset funds
- High risk: Axis Midcap, Mirae Tax Saver, Kotak Flexicap

TECHNICAL IMPLEMENTATION
------------------------

Technology Stack:
- Python 3.11 (pandas, numpy, scipy, matplotlib, seaborn)
- SQLite3 database
- Power BI Desktop for visualization
- Git for version control

Data Pipeline:
- Raw data: 10 CSV files (320 MB)
- Processed: 10 cleaned CSVs
- Database: 22 tables, 87,533 records
- Outputs: Reports, dashboards, analytics

Quality Assurance:
- All AMFI codes validated (40/40 match)
- Date continuity verified
- Data type consistency checked
- Formula accuracy tested

INSIGHTS & RECOMMENDATIONS
---------------------------

For Investors:
1. SIP is reliable - 99.97% continuity rate shows investor trust
2. Diversify across categories - concentrated portfolios (HHI > 0.20) have higher volatility
3. Risk-based selection - use Sharpe ratio and fund scorecard for decision making
4. Long-term perspective - CAGR over 3 years superior to 1-year returns

For Fund Houses:
1. SIP growth opportunities - only 0.03% at-risk investors despite market volatility
2. Geographic expansion - T30 cities have 65.9% but B30 potential remains
3. Fee competitiveness - expense ratio inversely correlated with inflows
4. Category diversification - category inflows show emerging trends (Flexi Cap growth)

For Regulators:
1. Market health - strong SIP continuity indicates retail participation confidence
2. Concentration risk - 9 equity funds have HHI > 0.15 (monitoring needed)
3. Investor protection - elderly (60+) group shows lower SIP amounts (Rs 1,200 avg)

LIMITATIONS & FUTURE WORK
--------------------------

Current Limitations:
- Data limited to 2022-2026 period
- Real-time NAV updates limited to 6 schemes
- Recommender system uses simple Sharpe ranking
- No macroeconomic factors considered

Future Enhancements:
- Machine learning for portfolio optimization (Markowitz efficient frontier)
- Monte Carlo simulations for NAV projections
- Sentiment analysis on scheme reviews
- Automated email alerts for VaR breaches
- Mobile app integration for investor tracking
- Integration with insurance products

CONCLUSION
----------

This comprehensive analytics platform successfully demonstrates data engineering, analytical, and visualization skills. The platform processes real financial data, generates actionable insights, and provides interactive dashboards for decision-making. All deliverables meet quality standards with no manual interventions required.

The project showcases proficiency in:
- ETL pipeline development
- Database design and SQL
- Statistical analysis and financial metrics
- Data visualization and storytelling
- Risk management and portfolio analysis

---

Report Generated: July 2026
Analysis Period: January 2022 - December 2025
Database Size: 12.42 MB
Total Records: 87,533
Processing Time: Automated pipeline < 5 minutes
