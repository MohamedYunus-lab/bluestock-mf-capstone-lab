"""
Day 6: Advanced Analytics + Risk Metrics
Author: Mohamed Yunus
Date: June 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import sqlite3
import os
from datetime import timedelta

conn = sqlite3.connect('bluestock_mf.db')

nav_history = pd.read_sql("SELECT * FROM fact_nav", conn)
fund_master = pd.read_sql("SELECT * FROM dim_fund", conn)
investor_transactions = pd.read_sql("SELECT * FROM fact_transactions", conn)
portfolio_holdings = pd.read_sql("SELECT * FROM fact_portfolio", conn)

conn.close()

nav_history['date'] = pd.to_datetime(nav_history['date'])
investor_transactions['transaction_date'] = pd.to_datetime(investor_transactions['transaction_date'])
portfolio_holdings['portfolio_date'] = pd.to_datetime(portfolio_holdings['portfolio_date'])

nav_history = nav_history.sort_values(['amfi_code', 'date'])

os.makedirs('reports/advanced', exist_ok=True)

print("\n" + "="*80)
print("TASK 1: Historical VaR (95%) and CVaR Computation")
print("="*80)

nav_history['daily_return'] = nav_history.groupby('amfi_code')['nav'].pct_change()

var_cvar_results = []

for code in fund_master['amfi_code']:
    fund_data = nav_history[nav_history['amfi_code'] == code].copy()
    fund_name = fund_master[fund_master['amfi_code'] == code]['scheme_name'].values[0]
    
    returns = fund_data['daily_return'].dropna()
    
    if len(returns) > 0:
        var_95 = np.percentile(returns, 5)
        cvar = returns[returns <= var_95].mean()
    else:
        var_95 = np.nan
        cvar = np.nan
    
    var_cvar_results.append({
        'amfi_code': code,
        'scheme_name': fund_name,
        'var_95': var_95 * 100,
        'cvar': cvar * 100
    })

var_cvar_df = pd.DataFrame(var_cvar_results)
var_cvar_df = var_cvar_df.sort_values('var_95')

print(f"VaR and CVaR computed for all funds")
print(f"\nTop 5 funds with highest VaR (highest risk):")
print(var_cvar_df.tail(5)[['scheme_name', 'var_95', 'cvar']])

var_cvar_df.to_csv('reports/advanced/var_cvar_report.csv', index=False)

print("\n" + "="*80)
print("TASK 2: Rolling 90-Day Sharpe Ratio")
print("="*80)

key_codes = fund_master.nlargest(5, 'amfi_code')['amfi_code'].head(5).tolist()

plt.figure(figsize=(14, 8))

for code in key_codes:
    fund_data = nav_history[nav_history['amfi_code'] == code].copy()
    fund_name = fund_master[fund_master['amfi_code'] == code]['scheme_name'].values[0]
    
    fund_data = fund_data.sort_values('date')
    fund_data['daily_return'] = fund_data['nav'].pct_change()
    
    rf_rate = 6.5 / 100
    daily_rf = rf_rate / 252
    
    fund_data['excess_return'] = fund_data['daily_return'] - daily_rf
    
    rolling_mean = fund_data['excess_return'].rolling(window=90).mean()
    rolling_std = fund_data['excess_return'].rolling(window=90).std()
    rolling_sharpe = (rolling_mean / rolling_std) * np.sqrt(252)
    
    plt.plot(fund_data['date'], rolling_sharpe, label=fund_name[:30], linewidth=2)

plt.title('Rolling 90-Day Sharpe Ratio - Top 5 Funds', fontsize=14, fontweight='bold')
plt.xlabel('Date', fontsize=12)
plt.ylabel('Rolling Sharpe Ratio', fontsize=12)
plt.legend(loc='best', fontsize=9)
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig('reports/advanced/rolling_sharpe_chart.png', dpi=300, bbox_inches='tight')

print(f"Rolling Sharpe ratio computed for 5 key funds")
print(f"Chart saved to reports/advanced/rolling_sharpe_chart.png")

print("\n" + "="*80)
print("TASK 3: Investor Cohort Analysis")
print("="*80)

investor_transactions['year'] = pd.to_datetime(investor_transactions['transaction_date']).dt.year

cohort_analysis = investor_transactions.groupby('year').agg({
    'investor_id': 'count',
    'amount_inr': ['sum', 'mean']
}).round(2)

cohort_analysis.columns = ['transaction_count', 'total_invested_cr', 'avg_sip_amount']

cohort_results = []

for year in sorted(investor_transactions['year'].unique()):
    year_data = investor_transactions[investor_transactions['year'] == year]
    
    total_invested = year_data['amount_inr'].sum()
    avg_sip = year_data['amount_inr'].mean()
    
    top_fund = year_data['amfi_code'].value_counts().index[0]
    top_fund_name = fund_master[fund_master['amfi_code'] == top_fund]['scheme_name'].values[0]
    
    cohort_results.append({
        'year': year,
        'investor_count': year_data['investor_id'].nunique(),
        'total_invested_cr': total_invested,
        'avg_sip_amount': avg_sip,
        'top_fund': top_fund_name,
        'transaction_count': len(year_data)
    })

cohort_df = pd.DataFrame(cohort_results)

print(f"Investor cohort analysis completed")
print(f"\nCohort Summary:")
print(cohort_df)

print("\n" + "="*80)
print("TASK 4: SIP Continuity Analysis")
print("="*80)

sip_investors = investor_transactions.groupby('investor_id').size()
sip_investors_6plus = sip_investors[sip_investors >= 6].index

at_risk_count = 0
continuity_results = []

for investor_id in sip_investors_6plus:
    investor_data = investor_transactions[investor_transactions['investor_id'] == investor_id].sort_values('transaction_date')
    
    if len(investor_data) >= 2:
        dates = pd.to_datetime(investor_data['transaction_date']).values
        gaps = np.diff(dates) / np.timedelta64(1, 'D')
        
        avg_gap = np.mean(gaps)
        max_gap = np.max(gaps)
        
        if max_gap > 35:
            at_risk_count += 1
        
        continuity_results.append({
            'investor_id': investor_id,
            'sip_count': len(investor_data),
            'avg_gap_days': avg_gap,
            'max_gap_days': max_gap,
            'at_risk': max_gap > 35
        })

continuity_df = pd.DataFrame(continuity_results)

total_sip_investors = len(sip_investors_6plus)
continuity_rate = ((total_sip_investors - at_risk_count) / total_sip_investors * 100) if total_sip_investors > 0 else 0

print(f"SIP continuity analysis for {total_sip_investors} investors with 6+ SIP transactions")
print(f"At-risk investors (gap > 35 days): {at_risk_count}")
print(f"Continuity rate: {continuity_rate:.2f}%")
print(f"\nSample at-risk investors:")
print(continuity_df[continuity_df['at_risk'] == True].head(10))

print("\n" + "="*80)
print("TASK 5: Fund Recommender System")
print("="*80)

performance_metrics = pd.read_csv('reports/performance/fund_scorecard.csv')

risk_mapping = {
    'Low': ['Liquid', 'Gilt', 'Short Duration', 'Debt'],
    'Moderate': ['Balanced', 'Conservative', 'Multi-Asset'],
    'High': ['Equity', 'Midcap', 'Smallcap', 'Flexi Cap']
}

def recommend_funds(risk_appetite):
    if risk_appetite not in risk_mapping:
        return pd.DataFrame()
    
    risk_categories = risk_mapping[risk_appetite]
    
    filtered_funds = fund_master[fund_master['category'].isin(risk_categories)].copy()
    
    filtered_funds = filtered_funds.merge(
        performance_metrics[['scheme_name', 'sharpe_ratio']],
        left_on='scheme_name',
        right_on='scheme_name',
        how='inner'
    )
    
    top_3 = filtered_funds.nlargest(3, 'sharpe_ratio')[['scheme_name', 'category', 'expense_ratio_pct', 'sharpe_ratio']]
    
    return top_3

print(f"\nFund Recommender - Risk Appetite Based")
print(f"\nRecommendations for LOW risk appetite:")
low_risk_rec = recommend_funds('Low')
print(low_risk_rec)

print(f"\nRecommendations for MODERATE risk appetite:")
moderate_risk_rec = recommend_funds('Moderate')
print(moderate_risk_rec)

print(f"\nRecommendations for HIGH risk appetite:")
high_risk_rec = recommend_funds('High')
print(high_risk_rec)

print("\n" + "="*80)
print("TASK 6: Sector HHI Concentration Analysis")
print("="*80)

hhi_results = []

equity_categories = ['Equity', 'Midcap', 'Smallcap', 'Largecap', 'Flexicap']
equity_funds = fund_master[fund_master['category'].isin(equity_categories)]['amfi_code'].tolist()

for code in equity_funds:
    fund_holdings = portfolio_holdings[portfolio_holdings['amfi_code'] == code].copy()
    fund_name = fund_master[fund_master['amfi_code'] == code]['scheme_name'].values[0]
    
    if len(fund_holdings) > 0:
        weights = fund_holdings['weight_pct'].values / 100
        hhi = np.sum(weights ** 2)
    else:
        hhi = 0
    
    concentration_level = 'High' if hhi > 0.15 else ('Moderate' if hhi > 0.08 else 'Low')
    
    hhi_results.append({
        'amfi_code': code,
        'scheme_name': fund_name,
        'hhi_index': hhi,
        'concentration': concentration_level,
        'holdings_count': len(fund_holdings)
    })

hhi_df = pd.DataFrame(hhi_results)
hhi_df = hhi_df.sort_values('hhi_index', ascending=False)

print(f"Sector HHI concentration computed for {len(hhi_df)} equity funds")
print(f"\nTop 5 most concentrated portfolios:")
print(hhi_df.head(5)[['scheme_name', 'hhi_index', 'concentration', 'holdings_count']])

print("\n" + "="*80)
print("ADVANCED ANALYTICS SUMMARY")
print("="*80)

print(f"\n1. VaR/CVaR Analysis:")
print(f"   - Riskiest fund (highest VaR): {var_cvar_df.iloc[-1]['scheme_name']}")
print(f"   - VaR at 95%: {var_cvar_df.iloc[-1]['var_95']:.2f}%")

print(f"\n2. Rolling Sharpe Ratio:")
print(f"   - Computed for top 5 funds over 90-day rolling windows")
print(f"   - Chart saved showing performance trends")

print(f"\n3. Investor Cohorts:")
print(f"   - Total cohorts analyzed: {len(cohort_df)}")
print(f"   - Highest investment year: {cohort_df.loc[cohort_df['total_invested_cr'].idxmax(), 'year']}")

print(f"\n4. SIP Continuity:")
print(f"   - Total SIP investors (6+ transactions): {total_sip_investors}")
print(f"   - At-risk investors: {at_risk_count}")
print(f"   - Continuity rate: {continuity_rate:.2f}%")

print(f"\n5. Portfolio Concentration:")
print(f"   - Highly concentrated funds: {len(hhi_df[hhi_df['concentration'] == 'High'])}")
print(f"   - Most concentrated: {hhi_df.iloc[0]['scheme_name']} (HHI: {hhi_df.iloc[0]['hhi_index']:.4f})")

print(f"\nAll reports saved to reports/advanced/ folder")
