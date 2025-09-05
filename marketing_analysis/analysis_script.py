import pandas as pd
import numpy as np
from datetime import datetime

# Read the CSV file
df = pd.read_csv(r'C:\Users\eunhe\Documents\eight_sleep_assessment\Raw Data\monthly_marketing_channel_level.csv')

# Clean the data
def clean_currency(value):
    if pd.isna(value) or value == '':
        return 0
    return float(str(value).replace('$', '').replace(',', '').strip())

def clean_number(value):
    if pd.isna(value) or value == '':
        return 0
    return float(str(value).replace(',', '').strip())

# Clean all numeric columns
df['Spend'] = df['Spend'].apply(clean_currency)
df['Visitors'] = df['Visitors'].apply(clean_number)
df['Last Click Add To Cart'] = df['Last Click Add To Cart'].apply(clean_number)
df['Last Click Orders'] = df['Last Click Orders'].apply(clean_number)
df['Last Click Revenue'] = df['Last Click Revenue'].apply(clean_currency)
df['Last Click Email Captures'] = df['Last Click Email Captures'].apply(clean_number)
df['Email capture conversions 30 day window'] = df['Email capture conversions 30 day window'].apply(clean_number)
df['Email capture conversions 60 day window'] = df['Email capture conversions 60 day window'].apply(clean_number)

# Convert Month to datetime
df['Month'] = pd.to_datetime(df['Month'])

# Calculate key metrics
df['ROAS'] = df['Last Click Revenue'] / df['Spend'].replace(0, np.nan)
df['CPA'] = df['Spend'] / df['Last Click Orders'].replace(0, np.nan)
df['Conversion_Rate'] = df['Last Click Orders'] / df['Visitors']
df['Email_Capture_Rate'] = df['Last Click Email Captures'] / df['Visitors']
df['Email_30d_Conv_Rate'] = df['Email capture conversions 30 day window'] / df['Last Click Email Captures'].replace(0, np.nan)
df['Email_60d_Conv_Rate'] = df['Email capture conversions 60 day window'] / df['Last Click Email Captures'].replace(0, np.nan)

# Filter out organic traffic for paid channel analysis
paid_channels = df[df['Spend'] > 0].copy()

print("=== MARKETING DATA ANALYSIS ===")
print("\n1. OVERALL CHANNEL PERFORMANCE")
print("-" * 50)

# Group by channel for summary stats
channel_summary = paid_channels.groupby('Channel').agg({
    'Spend': 'sum',
    'Last Click Revenue': 'sum',
    'Last Click Orders': 'sum',
    'Visitors': 'sum',
    'Last Click Email Captures': 'sum',
    'Email capture conversions 30 day window': 'sum',
    'Email capture conversions 60 day window': 'sum'
}).round(2)

# Calculate aggregated metrics
channel_summary['Avg_ROAS'] = channel_summary['Last Click Revenue'] / channel_summary['Spend']
channel_summary['Avg_CPA'] = channel_summary['Spend'] / channel_summary['Last Click Orders']
channel_summary['Overall_Conv_Rate'] = channel_summary['Last Click Orders'] / channel_summary['Visitors']
channel_summary['Overall_Email_Capture_Rate'] = channel_summary['Last Click Email Captures'] / channel_summary['Visitors']

print(channel_summary)

print("\n2. CHANNEL PERFORMANCE PROBLEMS")
print("-" * 50)

# Identify poor performing channels
poor_roas = channel_summary[channel_summary['Avg_ROAS'] < 2.0]
high_cpa = channel_summary[channel_summary['Avg_CPA'] > 1000]
low_conversion = channel_summary[channel_summary['Overall_Conv_Rate'] < 0.001]

print("Channels with ROAS < 2.0:")
for channel in poor_roas.index:
    roas = poor_roas.loc[channel, 'Avg_ROAS']
    spend = poor_roas.loc[channel, 'Spend']
    print(f"  {channel}: ROAS {roas:.2f}, Total Spend ${spend:,.0f}")

print("\nChannels with CPA > $1000:")
for channel in high_cpa.index:
    cpa = high_cpa.loc[channel, 'Avg_CPA']
    spend = high_cpa.loc[channel, 'Spend']
    print(f"  {channel}: CPA ${cpa:.0f}, Total Spend ${spend:,.0f}")

print("\n3. YOUTUBE EMAIL OPPORTUNITY ANALYSIS")
print("-" * 50)

youtube_data = paid_channels[paid_channels['Channel'] == 'YouTube Ads'].copy()
youtube_totals = youtube_data.agg({
    'Visitors': 'sum',
    'Last Click Email Captures': 'sum',
    'Email capture conversions 30 day window': 'sum',
    'Email capture conversions 60 day window': 'sum',
    'Last Click Orders': 'sum',
    'Spend': 'sum',
    'Last Click Revenue': 'sum'
})

print("YouTube Ads Current Performance:")
print(f"Total Visitors: {youtube_totals['Visitors']:,.0f}")
print(f"Total Email Captures: {youtube_totals['Last Click Email Captures']:,.0f}")
print(f"Email Capture Rate: {(youtube_totals['Last Click Email Captures'] / youtube_totals['Visitors'] * 100):.2f}%")
print(f"30-day Email Conversions: {youtube_totals['Email capture conversions 30 day window']:,.0f}")
print(f"60-day Email Conversions: {youtube_totals['Email capture conversions 60 day window']:,.0f}")
print(f"Direct Orders: {youtube_totals['Last Click Orders']:,.0f}")
print(f"Total Spend: ${youtube_totals['Spend']:,.0f}")
print(f"Current ROAS: {youtube_totals['Last Click Revenue'] / youtube_totals['Spend']:.2f}")

# Calculate email conversion rates
email_30d_rate = youtube_totals['Email capture conversions 30 day window'] / youtube_totals['Last Click Email Captures']
email_60d_rate = youtube_totals['Email capture conversions 60 day window'] / youtube_totals['Last Click Email Captures']

print(f"\nEmail Performance:")
print(f"30-day conversion rate from emails: {email_30d_rate * 100:.2f}%")
print(f"60-day conversion rate from emails: {email_60d_rate * 100:.2f}%")

# Compare to other channels' email capture rates
print(f"\nEmail Capture Rate Comparison:")
for channel in channel_summary.index:
    rate = channel_summary.loc[channel, 'Overall_Email_Capture_Rate'] * 100
    print(f"{channel}: {rate:.2f}%")

# Opportunity calculation
current_direct_orders = youtube_totals['Last Click Orders']
current_email_orders_60d = youtube_totals['Email capture conversions 60 day window']
total_attributed_orders = current_direct_orders + current_email_orders_60d

print(f"\nTotal YouTube attributed orders (direct + 60d email): {total_attributed_orders:,.0f}")
print(f"Direct orders represent {(current_direct_orders / total_attributed_orders * 100):.1f}% of total")
print(f"Email orders represent {(current_email_orders_60d / total_attributed_orders * 100):.1f}% of total")

print("\n4. MONTHLY PERFORMANCE TRENDS")
print("-" * 50)

# Look at monthly trends for each channel
monthly_perf = paid_channels.groupby(['Channel', 'Month']).agg({
    'ROAS': 'mean',
    'CPA': 'mean',
    'Spend': 'sum'
}).round(2)

print("Monthly ROAS by Channel:")
for channel in paid_channels['Channel'].unique():
    channel_data = monthly_perf.loc[channel]
    print(f"\n{channel}:")
    for month, data in channel_data.iterrows():
        print(f"  {month.strftime('%Y-%m')}: ROAS {data['ROAS']:.2f}, CPA ${data['CPA']:.0f}, Spend ${data['Spend']:,.0f}")

print("\n5. WORST PERFORMING MONTHS")
print("-" * 50)

# Identify worst performing month/channel combinations
worst_performers = paid_channels.nsmallest(10, 'ROAS')[['Channel', 'Month', 'ROAS', 'CPA', 'Spend', 'Last Click Orders']]
print("Top 10 worst ROAS performances:")
for idx, row in worst_performers.iterrows():
    print(f"{row['Channel']} {row['Month'].strftime('%Y-%m')}: ROAS {row['ROAS']:.2f}, Spend ${row['Spend']:,.0f}, Orders {row['Last Click Orders']}")