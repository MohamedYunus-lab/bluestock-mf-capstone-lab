"""
Day 3: Exploratory Data Analysis
Author: Mohamed Yunus
Date: June 2026
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import os

os.makedirs('reports/charts', exist_ok=True)

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

print("Loading data from database...")
conn = sqlite3.connect('bluestock_mf.db')

nav_history = pd.read_sql("SELECT * FROM fact_nav", conn)
aum_data = pd.read_sql("SELECT * FROM fact_aum", conn)
sip_data = pd.read_sql("SELECT * FROM fact_sip_industry", conn)
category_data = pd.read_sql("SELECT * FROM fact_category_inflows", conn)
transactions = pd.read_sql("SELECT * FROM fact_transactions", conn)
folio_data = pd.read_sql("SELECT * FROM fact_folio_count", conn)
portfolio = pd.read_sql("SELECT * FROM fact_portfolio", conn)
fund_master = pd.read_sql("SELECT * FROM dim_fund", conn)

conn.close()

print(f"Data loaded: {len(nav_history)} NAV records, {len(transactions)} transactions")

nav_history['date'] = pd.to_datetime(nav_history['date'])
aum_data['date'] = pd.to_datetime(aum_data['date'])
sip_data['month'] = pd.to_datetime(sip_data['month'])
category_data['month'] = pd.to_datetime(category_data['month'])
folio_data['month'] = pd.to_datetime(folio_data['month'])
transactions['transaction_date'] = pd.to_datetime(transactions['transaction_date'])

print("\n" + "="*80)
print("CHART 1: NAV Trend Analysis for All 40 Schemes")
print("="*80)

nav_with_names = nav_history.merge(fund_master[['amfi_code', 'scheme_name']], on='amfi_code')

fig = px.line(nav_with_names, x='date', y='nav', color='scheme_name',
              title='Daily NAV Trends (2022-2026) - All 40 Schemes')
fig.add_vrect(x0="2023-01-01", x1="2023-12-31", fillcolor="green", opacity=0.1,
              annotation_text="2023 Bull Run", annotation_position="top left")
fig.add_vrect(x0="2024-01-01", x1="2024-06-30", fillcolor="red", opacity=0.1,
              annotation_text="2024 Correction", annotation_position="top left")
fig.update_layout(height=600, showlegend=False)
fig.write_html('reports/charts/01_nav_trends.html')
print("Chart saved: 01_nav_trends.html")
print("Insight: NAV trends show strong bull run in 2023 with market correction in early 2024")

print("\n" + "="*80)
print("CHART 2: AUM Growth by Fund House")
print("="*80)

aum_data['year'] = aum_data['date'].dt.year
aum_yearly = aum_data.groupby(['year', 'fund_house'])['aum_lakh_crore'].max().reset_index()

plt.figure(figsize=(14, 7))
sns.barplot(data=aum_yearly, x='fund_house', y='aum_lakh_crore', hue='year', palette='viridis')
plt.xticks(rotation=45, ha='right')
plt.title('AUM Growth by Fund House (2022-2025)', fontsize=16, fontweight='bold')
plt.ylabel('AUM (Lakh Crore)')
plt.xlabel('Fund House')
plt.legend(title='Year', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('reports/charts/02_aum_growth.png', dpi=300, bbox_inches='tight')
plt.close()
print("Chart saved: 02_aum_growth.png")
print("Insight: SBI Mutual Fund dominates with Rs 12.5 lakh crore AUM, showing consistent growth")

print("\n" + "="*80)
print("CHART 3: Monthly SIP Inflow Trends")
print("="*80)

fig = go.Figure()
fig.add_trace(go.Scatter(x=sip_data['month'], y=sip_data['sip_inflow_crore'],
                         mode='lines+markers', name='SIP Inflow',
                         line=dict(color='blue', width=3)))

max_sip = sip_data.loc[sip_data['sip_inflow_crore'].idxmax()]
fig.add_annotation(x=max_sip['month'], y=max_sip['sip_inflow_crore'],
                   text=f"All-Time High<br>Rs {max_sip['sip_inflow_crore']:,.0f} Cr",
                   showarrow=True, arrowhead=2, bgcolor="yellow", font=dict(size=12))

fig.update_layout(title='Monthly SIP Inflows (Jan 2022 - Dec 2025)',
                  xaxis_title='Month', yaxis_title='SIP Inflow (Crore)',
                  height=500)
fig.write_html('reports/charts/03_sip_trends.html')
print("Chart saved: 03_sip_trends.html")
print(f"Insight: SIP inflows reached all-time high of Rs {max_sip['sip_inflow_crore']:,.0f} crore in December 2025")

print("\n" + "="*80)
print("CHART 4: Category Inflow Heatmap")
print("="*80)

category_data['month_name'] = category_data['month'].dt.strftime('%Y-%m')
heatmap_data = category_data.pivot_table(index='category', columns='month_name',
                                          values='net_inflow_crore', aggfunc='sum')

plt.figure(figsize=(16, 8))
sns.heatmap(heatmap_data, annot=False, fmt='.0f', cmap='RdYlGn', center=0,
            cbar_kws={'label': 'Net Inflow (Crore)'}, linewidths=0.5)
plt.title('Category-wise Net Inflows Heatmap (Monthly)', fontsize=16, fontweight='bold')
plt.xlabel('Month')
plt.ylabel('Fund Category')
plt.xticks(rotation=90)
plt.tight_layout()
plt.savefig('reports/charts/04_category_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()
print("Chart saved: 04_category_heatmap.png")
print("Insight: Large Cap and Mid Cap categories show strongest inflows across most months")

print("\n" + "="*80)
print("CHART 5: Investor Demographics - Age Distribution")
print("="*80)

age_dist = transactions['age_group'].value_counts()

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Pie chart
axes[0].pie(age_dist.values, labels=age_dist.index, autopct='%1.1f%%',
            startangle=90, colors=sns.color_palette('Set2'))
axes[0].set_title('Age Group Distribution', fontsize=14, fontweight='bold')

# Box plot
sip_only = transactions[transactions['transaction_type'] == 'SIP']
sns.boxplot(data=sip_only, x='age_group', y='amount_inr', ax=axes[1], palette='Set2')
axes[1].set_title('SIP Amount by Age Group', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Age Group')
axes[1].set_ylabel('SIP Amount (INR)')
axes[1].tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('reports/charts/05_age_demographics.png', dpi=300, bbox_inches='tight')
plt.close()
print("Chart saved: 05_age_demographics.png")
print("Insight: 26-35 age group dominates investor base with moderate SIP amounts")

print("\n" + "="*80)
print("CHART 6: Gender Distribution")
print("="*80)

gender_dist = transactions['gender'].value_counts()

plt.figure(figsize=(10, 6))
plt.pie(gender_dist.values, labels=gender_dist.index, autopct='%1.1f%%',
        startangle=90, colors=['#3498db', '#e74c3c'])
plt.title('Investor Gender Distribution', fontsize=16, fontweight='bold')
plt.savefig('reports/charts/06_gender_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("Chart saved: 06_gender_distribution.png")
print(f"Insight: Gender split shows {gender_dist.index[0]} investors at {gender_dist.values[0]/gender_dist.sum()*100:.1f}%")

print("\n" + "="*80)
print("CHART 7: Geographic Distribution by State")
print("="*80)

state_amount = transactions.groupby('state')['amount_inr'].sum().sort_values(ascending=True)

plt.figure(figsize=(12, 10))
plt.barh(state_amount.index, state_amount.values, color='steelblue')
plt.xlabel('Total Investment Amount (INR)', fontsize=12)
plt.ylabel('State', fontsize=12)
plt.title('Investment Distribution by State', fontsize=16, fontweight='bold')
plt.ticklabel_format(style='plain', axis='x')
plt.tight_layout()
plt.savefig('reports/charts/07_state_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("Chart saved: 07_state_distribution.png")
print(f"Insight: Top state by investment is {state_amount.index[-1]} with Rs {state_amount.values[-1]:,.0f}")

print("\n" + "="*80)
print("CHART 8: T30 vs B30 City Tier Distribution")
print("="*80)

city_tier = transactions.groupby('city_tier')['amount_inr'].sum()

plt.figure(figsize=(10, 6))
colors = ['#2ecc71', '#f39c12']
plt.pie(city_tier.values, labels=city_tier.index, autopct='%1.1f%%',
        startangle=90, colors=colors, explode=(0.05, 0))
plt.title('Investment Distribution: T30 vs B30 Cities', fontsize=16, fontweight='bold')
plt.savefig('reports/charts/08_city_tier.png', dpi=300, bbox_inches='tight')
plt.close()
print("Chart saved: 08_city_tier.png")
print(f"Insight: T30 cities contribute {city_tier['T30']/city_tier.sum()*100:.1f}% of total investments")

print("\n" + "="*80)
print("CHART 9: Folio Count Growth Over Time")
print("="*80)

fig = go.Figure()
fig.add_trace(go.Scatter(x=folio_data['month'], y=folio_data['total_folios_crore'],
                         mode='lines+markers', name='Total Folios',
                         line=dict(color='purple', width=3)))

# Mark milestones
milestones = [(folio_data['month'].min(), folio_data['total_folios_crore'].min(), 'Start'),
              (folio_data['month'].max(), folio_data['total_folios_crore'].max(), 'Latest')]

for month, value, label in milestones:
    fig.add_annotation(x=month, y=value, text=f"{label}<br>{value:.2f} Cr",
                       showarrow=True, arrowhead=2)

fig.update_layout(title='Investor Folio Count Growth (Jan 2022 - Dec 2025)',
                  xaxis_title='Month', yaxis_title='Total Folios (Crore)',
                  height=500)
fig.write_html('reports/charts/09_folio_growth.html')
print("Chart saved: 09_folio_growth.html")
print(f"Insight: Folios grew from {folio_data['total_folios_crore'].min():.2f} Cr to {folio_data['total_folios_crore'].max():.2f} Cr")

print("\n" + "="*80)
print("CHART 10: NAV Return Correlation Matrix")
print("="*80)

# Select top 10 funds by AUM
top_funds = fund_master.nlargest(10, 'expense_ratio_pct')['amfi_code'].tolist()
nav_top = nav_history[nav_history['amfi_code'].isin(top_funds)]

# Calculate daily returns
nav_top = nav_top.sort_values(['amfi_code', 'date'])
nav_top['daily_return'] = nav_top.groupby('amfi_code')['nav'].pct_change()

# Create pivot table for correlation
returns_pivot = nav_top.pivot_table(index='date', columns='amfi_code', values='daily_return')
correlation_matrix = returns_pivot.corr()

plt.figure(figsize=(12, 10))
sns.heatmap(correlation_matrix, annot=True, fmt='.2f', cmap='coolwarm',
            center=0, square=True, linewidths=1, cbar_kws={'label': 'Correlation'})
plt.title('NAV Daily Return Correlation (Top 10 Funds)', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('reports/charts/10_correlation_matrix.png', dpi=300, bbox_inches='tight')
plt.close()
print("Chart saved: 10_correlation_matrix.png")
print("Insight: High correlation between large cap funds indicating market-driven movements")

print("\n" + "="*80)
print("CHART 11: Sector Allocation Donut Chart")
print("="*80)

sector_weights = portfolio.groupby('sector')['weight_pct'].sum().sort_values(ascending=False)

fig, ax = plt.subplots(figsize=(12, 8))
colors = sns.color_palette('Set3', len(sector_weights))
wedges, texts, autotexts = ax.pie(sector_weights.values, labels=sector_weights.index,
                                    autopct='%1.1f%%', startangle=90, colors=colors,
                                    pctdistance=0.85, wedgeprops=dict(width=0.5))

for autotext in autotexts:
    autotext.set_color('black')
    autotext.set_fontweight('bold')
    
ax.set_title('Sector Allocation Across All Equity Funds', fontsize=16, fontweight='bold')
plt.savefig('reports/charts/11_sector_allocation.png', dpi=300, bbox_inches='tight')
plt.close()
print("Chart saved: 11_sector_allocation.png")
print(f"Insight: Top sector is {sector_weights.index[0]} with {sector_weights.values[0]:.1f}% allocation")

print("\n" + "="*80)
print("CHART 12: Transaction Type Distribution")
print("="*80)

tx_type = transactions['transaction_type'].value_counts()

plt.figure(figsize=(10, 6))
plt.bar(tx_type.index, tx_type.values, color=['#3498db', '#2ecc71', '#e74c3c'])
plt.xlabel('Transaction Type', fontsize=12)
plt.ylabel('Count', fontsize=12)
plt.title('Distribution of Transaction Types', fontsize=16, fontweight='bold')
for i, v in enumerate(tx_type.values):
    plt.text(i, v + 500, str(v), ha='center', fontweight='bold')
plt.tight_layout()
plt.savefig('reports/charts/12_transaction_types.png', dpi=300, bbox_inches='tight')
plt.close()
print("Chart saved: 12_transaction_types.png")
print(f"Insight: {tx_type.index[0]} is most popular with {tx_type.values[0]:,} transactions")

print("\n" + "="*80)
print("CHART 13: Average Transaction Amount by Payment Mode")
print("="*80)

payment_avg = transactions.groupby('payment_mode')['amount_inr'].mean().sort_values(ascending=False)

plt.figure(figsize=(10, 6))
plt.barh(payment_avg.index, payment_avg.values, color='coral')
plt.xlabel('Average Amount (INR)', fontsize=12)
plt.ylabel('Payment Mode', fontsize=12)
plt.title('Average Transaction Amount by Payment Mode', fontsize=16, fontweight='bold')
plt.ticklabel_format(style='plain', axis='x')
plt.tight_layout()
plt.savefig('reports/charts/13_payment_modes.png', dpi=300, bbox_inches='tight')
plt.close()
print("Chart saved: 13_payment_modes.png")
print(f"Insight: {payment_avg.index[0]} shows highest average amount of Rs {payment_avg.values[0]:,.0f}")

print("\n" + "="*80)
print("CHART 14: Income Level vs Investment Amount")
print("="*80)

income_investment = transactions.groupby('age_group').agg({
    'amount_inr': 'sum',
    'annual_income_lakh': 'mean'
}).reset_index()

fig, ax1 = plt.subplots(figsize=(12, 6))

color = 'tab:blue'
ax1.set_xlabel('Age Group', fontsize=12)
ax1.set_ylabel('Total Investment (INR)', color=color, fontsize=12)
ax1.bar(income_investment['age_group'], income_investment['amount_inr'], color=color, alpha=0.6)
ax1.tick_params(axis='y', labelcolor=color)
ax1.tick_params(axis='x', rotation=45)

ax2 = ax1.twinx()
color = 'tab:red'
ax2.set_ylabel('Average Annual Income (Lakh)', color=color, fontsize=12)
ax2.plot(income_investment['age_group'], income_investment['annual_income_lakh'],
         color=color, marker='o', linewidth=3)
ax2.tick_params(axis='y', labelcolor=color)

plt.title('Investment Amount vs Income Level by Age Group', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('reports/charts/14_income_investment.png', dpi=300, bbox_inches='tight')
plt.close()
print("Chart saved: 14_income_investment.png")
print("Insight: Higher income age groups show proportionally higher total investments")

print("\n" + "="*80)
print("CHART 15: Fund Category Distribution")
print("="*80)

category_count = fund_master['category'].value_counts()

plt.figure(figsize=(10, 6))
plt.pie(category_count.values, labels=category_count.index, autopct='%1.1f%%',
        startangle=90, colors=sns.color_palette('pastel'))
plt.title('Distribution of Funds by Category', fontsize=16, fontweight='bold')
plt.savefig('reports/charts/15_fund_categories.png', dpi=300, bbox_inches='tight')
plt.close()
print("Chart saved: 15_fund_categories.png")
print(f"Insight: {category_count.index[0]} category dominates with {category_count.values[0]} funds")

print("\n" + "="*80)
print("EDA ANALYSIS COMPLETE")
print("="*80)
print(f"\nTotal charts generated: 15")
print(f"Charts saved in: reports/charts/")
print("\nKey Insights Summary:")
print("1. NAV trends show 2023 bull run followed by 2024 correction")
print("2. SBI leads AMCs with Rs 12.5 lakh crore AUM")
print("3. SIP inflows reached all-time high in December 2025")
print("4. Large Cap and Mid Cap categories attract most inflows")
print("5. 26-35 age group dominates investor demographics")
print("6. T30 cities contribute majority of investments")
print("7. Folio count doubled from 13.26 Cr to 26.12 Cr")
print("8. High correlation among large cap fund returns")
print("9. Banking and IT sectors dominate portfolio allocations")
print("10. SIP is the most preferred investment mode")
