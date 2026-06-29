Bluestock Fintech - Mutual Fund Analytics Platform
Capstone Project Documentation

Author: Mohamed Yunus
Role: Data Analysis Intern
Date: June 2026

--------------------------------------------------------------------------------

PROJECT OVERVIEW

This project analyzes India's mutual fund industry by building a data pipeline that processes information from AMFI India. The system handles 40 mutual fund schemes across 10 major fund houses, covering over 87,000 records of NAV history, transactions, and performance metrics.

The work completed so far includes data ingestion from multiple sources, cleaning and standardization, database design with proper schema, and validation of data quality.

--------------------------------------------------------------------------------

WHAT THE PROJECT DOES

1. Collects data from AMFI India and public APIs
2. Cleans and standardizes the datasets
3. Stores everything in a SQLite database
4. Provides SQL queries for analysis
5. Validates data integrity across all sources

--------------------------------------------------------------------------------

DATASETS USED

Ten main datasets totaling 87,533 records:

Fund Master - 40 schemes with details like fund house, category, expense ratio
NAV History - 46,000 daily NAV records from January 2022 to May 2026
AUM by Fund House - 90 quarterly records for top 10 AMCs
Monthly SIP Inflows - 48 months of industry SIP data
Category Inflows - 144 records of category-wise flows
Industry Folio Count - 21 records showing investor folio statistics
Scheme Performance - 40 records with returns and risk metrics
Investor Transactions - 32,778 SIP, lumpsum and redemption records
Portfolio Holdings - 322 records of top equity holdings
Benchmark Indices - 8,050 daily index values for comparison

All data sourced from publicly available AMFI publications and mfapi.in API.

--------------------------------------------------------------------------------

HOW TO RUN THE CODE

Prerequisites:
- Python 3.10 or higher
- Internet connection for API calls

Step 1: Install required packages
Run: pip install -r requirements.txt

Step 2: Load and validate raw data
Run: python data_ingestion.py
This loads all CSV files, prints their structure, explores fund master data, and validates AMFI codes.

Step 3: Fetch live NAV from API
Run: python live_nav_fetch.py
This connects to mfapi.in and downloads historical NAV for 6 major schemes.

Step 4: Clean the data
Run: python data_cleaning.py
This standardizes column names, converts dates, handles missing values, and saves cleaned files.

Step 5: Create database
Run: python load_to_sqlite.py
This creates the SQLite database, loads all cleaned data, and verifies record counts.

The final database file is bluestock_mf.db (12.42 MB).

--------------------------------------------------------------------------------

PROJECT STRUCTURE

bluestock-mf-capstone/
  data/
    raw/ - Original CSV files and live NAV data
    processed/ - Cleaned CSV files ready for database
  sql/
    schema.sql - Database table definitions
    queries.sql - Analytical queries for insights
  reports/
    data_dictionary.md - Column descriptions
  data_ingestion.py - Loads and validates raw data
  live_nav_fetch.py - Fetches NAV from mfapi.in API
  data_cleaning.py - Cleans and standardizes data
  load_to_sqlite.py - Creates and populates database
  requirements.txt - Python dependencies
  bluestock_mf.db - SQLite database

--------------------------------------------------------------------------------

DATABASE DESIGN

The database uses a star schema with one dimension table and nine fact tables.

Dimension table:
dim_fund - 40 fund schemes with metadata

Fact tables:
fact_nav - 46,000 NAV records
fact_transactions - 32,778 investor transactions
fact_performance - 40 performance metrics
fact_portfolio - 322 holdings records
fact_aum - 90 AUM records by fund house
fact_sip_industry - 48 monthly SIP statistics
fact_category_inflows - 144 category flow records
fact_folio_count - 21 folio statistics
fact_benchmark - 8,050 index values

Indexes created on AMFI codes and date fields for faster queries.

--------------------------------------------------------------------------------

DATA VALIDATION RESULTS

AMFI Code Check: PASSED
All 40 schemes in fund master have matching NAV history records. No orphan records found.

Date Coverage:
Start: January 3, 2022
End: May 29, 2026
Trading days: 1,150

Fund Coverage:
10 fund houses including SBI, HDFC, ICICI Prudential, Nippon India, Kotak Mahindra
Categories: Equity and Debt
Sub-categories: 12 types including Large Cap, Mid Cap, Small Cap, ELSS, Liquid, Gilt
Risk grades: Low, Moderate, Moderately High, High, Very High

--------------------------------------------------------------------------------

SQL QUERIES INCLUDED

Ten analytical queries written in queries.sql:

1. Top 5 funds by AUM
2. Average NAV trends by month
3. SIP inflow year-over-year growth
4. Transaction volume by state
5. Funds with expense ratio below 1%
6. Best performing funds by Sharpe ratio
7. Fund house AUM rankings
8. Category-wise inflows last 6 months
9. High-risk high-return fund analysis
10. Investor demographics breakdown

--------------------------------------------------------------------------------

TECHNOLOGY STACK

Python 3.10 - Core programming language
Pandas 2.0 - Data manipulation and cleaning
NumPy 1.24 - Numerical operations
SQLite3 - Database engine
SQLAlchemy 2.0 - Database connectivity
Requests 2.30 - API integration
Git - Version control

--------------------------------------------------------------------------------

GITHUB REPOSITORY

Repository: github.com/MohamedYunus-lab/bluestock-mf-capstone-lab

Contains all source code, SQL scripts, and documentation with proper commit history.

--------------------------------------------------------------------------------

NEXT STEPS

Day 3: Exploratory data analysis with visualizations
Day 4: Calculate performance metrics like Sharpe, Alpha, Beta
Day 5: Build Power BI dashboard
Day 6: Advanced analytics and risk calculations
Day 7: Final report and presentation

--------------------------------------------------------------------------------

NOTES

All column names standardized to lowercase with underscores for consistency.
Date fields properly converted to datetime format.
Missing values handled appropriately during cleaning.
Database indexed for fast query performance.
Code follows standard Python conventions.

--------------------------------------------------------------------------------

Contact: Mohamed Yunus
Project: Bluestock Fintech MF Analytics
Status: Days 1-2 Complete

This project is for educational purposes only. Data sourced from publicly available AMFI India publications.
