"""
Day 4: Fund Performance Analytics
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

print("Loading data from database...")
conn = sqlite3.connect('bluestock_mf.db')

nav_history = pd.read_sql("SELECT * FROM fact_nav", conn)
fund_master = pd.read_sql("SELECT * FROM dim_fund", conn)
benchmark = pd.read_sql("SELECT * FROM fact_benchmark WHERE index_name='NIFTY100'", conn)
nifty50 = pd.read_sql("SELECT * FROM fact_benchmark WHERE index_name='NIFTY50'", conn)

conn.close()

nav_history['date'] = pd.to_datetime(nav_history['date'])
benchmark['date'] = pd.to_datetime(benchmark['date'])
nifty50['date'] = pd.to_datetime(nifty50['date'])

nav_history = nav_history.sort_values(['amfi_code', 'date'])

print(f"Data loaded: {len(nav_history)} NAV records, {len(fund_master)} funds")
os.makedirs('reports/performance', exist_ok=True)

print("\n" + "="*80)
print("TASK 1: Computing Daily Returns")
print("="*80)

nav_history['daily_return'] = nav_history.groupby('amfi_code')['nav'].pct_change()
nav_history['daily_return_pct'] = nav_history['daily_return'] * 100

print(f"Daily returns computed for all schemes")
print(f"Return distribution stats:")
print(f"  Mean: {nav_history['daily_return_pct'].mean():.4f}%")
print(f"  Std Dev: {nav_history['daily_return_pct'].std():.4f}%")
print(f"  Min: {nav_history['daily_return_pct'].min():.2f}%")
print(f"  Max: {nav_history['daily_return_pct'].max():.2f}%")

print("\n" + "="*80)
print("TASK 2: Computing CAGR for 1yr, 3yr, 5yr")
print("="*80)

def calculate_cagr(df, years):
    end_date = df['date'].max()
    start_date = end_date - pd.DateOffset(years=years)
    
    df_period = df[df['date'] >= start_date]
    if len(df_period) < 2:
        return np.nan
    
    start_nav = df_period.iloc[0]['nav']
    end_nav = df_period.iloc[-1]['nav']
    
    actual_years = (df_period['date'].max() - df_period['date'].min()).days / 365.25
    if actual_years <= 0:
        return np.nan
    
    cagr = (pow(end_nav / start_nav, 1 / actual_years) - 1) * 100
    return cagr

cagr_results = []

for code in fund_master['amfi_code']:
    fund_data = nav_history[nav_history['amfi_code'] == code].copy()
    fund_name = fund_master[fund_master['amfi_code'] == code]['scheme_name'].values[0]
    
    cagr_1yr = calculate_cagr(fund_data, 1)
    cagr_3yr = calculate_cagr(fund_data, 3)
    cagr_5yr = calculate_cagr(fund_data, 5)
    
    cagr_results.append({
        'amfi_code': code,
        'scheme_name': fund_name,
        'cagr_1yr': cagr_1yr,
        'cagr_3yr': cagr_3yr,
        'cagr_5yr': cagr_5yr
    })

cagr_df = pd.DataFrame(cagr_results)
print(f"CAGR computed for all funds")
print(f"\nTop 5 funds by 3-year CAGR:")
print(cagr_df.nlargest(5, 'cagr_3yr')[['scheme_name', 'cagr_3yr']])

print("\n" + "="*80)
print("TASK 3: Computing Sharpe Ratio")
print("="*80)

rf_rate = 6.5 / 100
daily_rf = rf_rate / 252

sharpe_results = []

for code in fund_master['amfi_code']:
    fund_data = nav_history[nav_history['amfi_code'] == code].copy()
    fund_name = fund_master[fund_master['amfi_code'] == code]['scheme_name'].values[0]
    
    returns = fund_data['daily_return'].dropna()
    
    if len(returns) > 0:
        excess_returns = returns - daily_rf
        sharpe_ratio = (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)
    else:
        sharpe_ratio = np.nan
    
    sharpe_results.append({
        'amfi_code': code,
        'scheme_name': fund_name,
        'sharpe_ratio': sharpe_ratio
    })

sharpe_df = pd.DataFrame(sharpe_results)
sharpe_df['sharpe_rank'] = sharpe_df['sharpe_ratio'].rank(ascending=False)

print(f"Sharpe Ratio computed for all funds")
print(f"\nTop 5 funds by Sharpe Ratio:")
print(sharpe_df.nlargest(5, 'sharpe_ratio')[['scheme_name', 'sharpe_ratio']])

print("\n" + "="*80)
print("TASK 4: Computing Sortino Ratio")
print("="*80)

sortino_results = []

for code in fund_master['amfi_code']:
    fund_data = nav_history[nav_history['amfi_code'] == code].copy()
    fund_name = fund_master[fund_master['amfi_code'] == code]['scheme_name'].values[0]
    
    returns = fund_data['daily_return'].dropna()
    
    if len(returns) > 0:
        excess_returns = returns - daily_rf
        downside_returns = excess_returns[excess_returns < 0]
        
        if len(downside_returns) > 0:
            downside_std = downside_returns.std()
            sortino_ratio = (excess_returns.mean() / downside_std) * np.sqrt(252)
        else:
            sortino_ratio = np.nan
    else:
        sortino_ratio = np.nan
    
    sortino_results.append({
        'amfi_code': code,
        'scheme_name': fund_name,
        'sortino_ratio': sortino_ratio
    })

sortino_df = pd.DataFrame(sortino_results)
sortino_df['sortino_rank'] = sortino_df['sortino_ratio'].rank(ascending=False)

print(f"Sortino Ratio computed for all funds")
print(f"\nTop 5 funds by Sortino Ratio:")
print(sortino_df.nlargest(5, 'sortino_ratio')[['scheme_name', 'sortino_ratio']])

print("\n" + "="*80)
print("TASK 5: Computing Alpha and Beta")
print("="*80)

benchmark = benchmark.sort_values('date')
benchmark['bench_return'] = benchmark['close_value'].pct_change()

alpha_beta_results = []

for code in fund_master['amfi_code']:
    fund_data = nav_history[nav_history['amfi_code'] == code].copy()
    fund_name = fund_master[fund_master['amfi_code'] == code]['scheme_name'].values[0]
    
    merged = pd.merge(
        fund_data[['date', 'daily_return']],
        benchmark[['date', 'bench_return']],
        on='date',
        how='inner'
    )
    
    merged = merged.dropna()
    
    if len(merged) > 30:
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            merged['bench_return'],
            merged['daily_return']
        )
        
        beta = slope
        alpha = intercept * 252 * 100
    else:
        beta = np.nan
        alpha = np.nan
    
    alpha_beta_results.append({
        'amfi_code': code,
        'scheme_name': fund_name,
        'alpha': alpha,
        'beta': beta
    })

alpha_beta_df = pd.DataFrame(alpha_beta_results)
alpha_beta_df['alpha_rank'] = alpha_beta_df['alpha'].rank(ascending=False)

print(f"Alpha and Beta computed for all funds")
print(f"\nTop 5 funds by Alpha:")
print(alpha_beta_df.nlargest(5, 'alpha')[['scheme_name', 'alpha', 'beta']])

alpha_beta_df.to_csv('reports/performance/alpha_beta.csv', index=False)
print(f"\nSaved alpha_beta.csv to reports/performance/")

print("\n" + "="*80)
print("TASK 6: Computing Maximum Drawdown")
print("="*80)

drawdown_results = []

for code in fund_master['amfi_code']:
    fund_data = nav_history[nav_history['amfi_code'] == code].copy()
    fund_name = fund_master[fund_master['amfi_code'] == code]['scheme_name'].values[0]
    
    fund_data['running_max'] = fund_data['nav'].cummax()
    fund_data['drawdown'] = (fund_data['nav'] / fund_data['running_max'] - 1) * 100
    
    max_dd = fund_data['drawdown'].min()
    max_dd_date = fund_data[fund_data['drawdown'] == max_dd]['date'].values[0]
    
    drawdown_results.append({
        'amfi_code': code,
        'scheme_name': fund_name,
        'max_drawdown': max_dd,
        'max_dd_date': pd.to_datetime(max_dd_date)
    })

drawdown_df = pd.DataFrame(drawdown_results)
drawdown_df['dd_rank'] = drawdown_df['max_drawdown'].rank(ascending=True)

print(f"Maximum Drawdown computed for all funds")
print(f"\nTop 5 funds with lowest drawdown:")
print(drawdown_df.nlargest(5, 'max_drawdown')[['scheme_name', 'max_drawdown', 'max_dd_date']])

print("\n" + "="*80)
print("TASK 7: Fund Scorecard (0-100)")
print("="*80)

scorecard = cagr_df[['amfi_code', 'scheme_name', 'cagr_3yr']].copy()
scorecard = scorecard.merge(sharpe_df[['amfi_code', 'sharpe_ratio', 'sharpe_rank']], on='amfi_code')
scorecard = scorecard.merge(alpha_beta_df[['amfi_code', 'alpha', 'alpha_rank']], on='amfi_code')
scorecard = scorecard.merge(drawdown_df[['amfi_code', 'max_drawdown', 'dd_rank']], on='amfi_code')

scorecard = scorecard.merge(
    fund_master[['amfi_code', 'expense_ratio_pct']],
    on='amfi_code',
    how='left'
)

scorecard['return_rank'] = scorecard['cagr_3yr'].rank(ascending=False)
scorecard['expense_rank'] = scorecard['expense_ratio_pct'].rank(ascending=True)

scorecard['return_rank_norm'] = (scorecard['return_rank'].max() - scorecard['return_rank'] + 1) / scorecard['return_rank'].max()
scorecard['sharpe_rank_norm'] = (scorecard['sharpe_rank'].max() - scorecard['sharpe_rank'] + 1) / scorecard['sharpe_rank'].max()
scorecard['alpha_rank_norm'] = (scorecard['alpha_rank'].max() - scorecard['alpha_rank'] + 1) / scorecard['alpha_rank'].max()
scorecard['expense_rank_norm'] = (scorecard['expense_rank'].max() - scorecard['expense_rank'] + 1) / scorecard['expense_rank'].max()
scorecard['dd_rank_norm'] = (scorecard['dd_rank'].max() - scorecard['dd_rank'] + 1) / scorecard['dd_rank'].max()

scorecard['composite_score'] = (
    0.30 * scorecard['return_rank_norm'] +
    0.25 * scorecard['sharpe_rank_norm'] +
    0.20 * scorecard['alpha_rank_norm'] +
    0.15 * scorecard['expense_rank_norm'] +
    0.10 * scorecard['dd_rank_norm']
) * 100

scorecard = scorecard.sort_values('composite_score', ascending=False)

print(f"Fund Scorecard computed for all funds")
print(f"\nTop 10 funds by Composite Score:")
print(scorecard[['scheme_name', 'composite_score', 'cagr_3yr', 'sharpe_ratio']].head(10))

scorecard.to_csv('reports/performance/fund_scorecard.csv', index=False)
print(f"\nSaved fund_scorecard.csv to reports/performance/")

print("\n" + "="*80)
print("TASK 8: Benchmark Comparison Chart")
print("="*80)

top5_codes = scorecard.head(5)['amfi_code'].tolist()

plt.figure(figsize=(14, 8))

end_date = nav_history['date'].max()
start_date = end_date - pd.DateOffset(years=3)

for code in top5_codes:
    fund_data = nav_history[
        (nav_history['amfi_code'] == code) & 
        (nav_history['date'] >= start_date)
    ].copy()
    
    fund_name = fund_master[fund_master['amfi_code'] == code]['scheme_name'].values[0]
    
    fund_data['indexed_nav'] = (fund_data['nav'] / fund_data['nav'].iloc[0]) * 100
    
    plt.plot(fund_data['date'], fund_data['indexed_nav'], label=fund_name[:30], linewidth=2)

nifty100_data = benchmark[benchmark['date'] >= start_date].copy()
nifty100_data['indexed'] = (nifty100_data['close_value'] / nifty100_data['close_value'].iloc[0]) * 100
plt.plot(nifty100_data['date'], nifty100_data['indexed'], 
         label='NIFTY 100', linewidth=2.5, linestyle='--', color='black')

nifty50_data = nifty50[nifty50['date'] >= start_date].copy()
nifty50_data['indexed'] = (nifty50_data['close_value'] / nifty50_data['close_value'].iloc[0]) * 100
plt.plot(nifty50_data['date'], nifty50_data['indexed'], 
         label='NIFTY 50', linewidth=2.5, linestyle=':', color='gray')

plt.title('Top 5 Funds vs Benchmark - 3 Year Performance (Indexed)', fontsize=14, fontweight='bold')
plt.xlabel('Date', fontsize=12)
plt.ylabel('Indexed Value (Base = 100)', fontsize=12)
plt.legend(loc='best', fontsize=9)
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig('reports/charts/16_benchmark_comparison.png', dpi=300, bbox_inches='tight')
print(f"Saved benchmark comparison chart to reports/charts/16_benchmark_comparison.png")

tracking_errors = []

for code in top5_codes:
    fund_data = nav_history[nav_history['amfi_code'] == code].copy()
    fund_name = fund_master[fund_master['amfi_code'] == code]['scheme_name'].values[0]
    
    merged = pd.merge(
        fund_data[['date', 'daily_return']],
        benchmark[['date', 'bench_return']],
        on='date',
        how='inner'
    )
    
    merged = merged.dropna()
    merged['excess_return'] = merged['daily_return'] - merged['bench_return']
    
    tracking_error = merged['excess_return'].std() * np.sqrt(252) * 100
    
    tracking_errors.append({
        'scheme_name': fund_name,
        'tracking_error': tracking_error
    })

te_df = pd.DataFrame(tracking_errors)
print(f"\nTracking Error vs NIFTY 100:")
print(te_df)

print("\n" + "="*80)
print("PERFORMANCE ANALYTICS COMPLETED")
print("="*80)
print(f"\nFiles generated:")
print(f"  1. reports/performance/fund_scorecard.csv")
print(f"  2. reports/performance/alpha_beta.csv")
print(f"  3. reports/charts/16_benchmark_comparison.png")
print(f"\nAll 8 tasks completed successfully")
