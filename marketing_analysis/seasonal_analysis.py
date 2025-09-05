import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('Raw Data/monthly_marketing_channel_level.csv')

# Clean the data
df['Spend_Clean'] = df['Spend'].str.replace('$', '').str.replace(',', '').str.replace(' ', '')
df['Spend_Clean'] = pd.to_numeric(df['Spend_Clean'], errors='coerce')
df['Revenue_Clean'] = pd.to_numeric(df['Last Click Revenue'], errors='coerce')
df['Month'] = pd.to_datetime(df['Month'])
df['Month_Num'] = df['Month'].dt.month
df['Year'] = df['Month'].dt.year

# Calculate key metrics
df['ROAS'] = df['Revenue_Clean'] / df['Spend_Clean']
df['Cost_Per_Order'] = df['Spend_Clean'] / df['Last Click Orders']
df['Conversion_Rate'] = (df['Last Click Orders'] / df['Visitors']) * 100

print('SEASONALITY ANALYSIS')
print('=' * 50)

# Seasonal patterns for paid channels
paid_df = df[df['Channel'].isin(['Google Ads', 'YouTube Ads', 'FB Ads'])].copy()

print('\nAVERAGE ROAS BY MONTH (All Paid Channels)')
seasonal_roas = paid_df.groupby('Month_Num')['ROAS'].mean().round(2)
for month, roas in seasonal_roas.items():
    month_name = pd.to_datetime(f'2024-{month:02d}-01').strftime('%B')
    print(f'{month_name}: {roas}')

print('\nAVERAGE SPEND BY MONTH (All Paid Channels)')
seasonal_spend = paid_df.groupby('Month_Num')['Spend_Clean'].mean().round(0)
for month, spend in seasonal_spend.items():
    month_name = pd.to_datetime(f'2024-{month:02d}-01').strftime('%B')
    print(f'{month_name}: ${spend:,.0f}')

print('\nORGANIC + DIRECT SEASONALITY')
print('=' * 35)
organic_df = df[df['Channel'] == 'Organic + Direct'].copy()
organic_seasonal = organic_df.groupby('Month_Num').agg({
    'Revenue_Clean': 'mean',
    'Last Click Orders': 'mean',
    'Conversion_Rate': 'mean'
}).round(2)

for month_num in organic_seasonal.index:
    month_name = pd.to_datetime(f'2024-{month_num:02d}-01').strftime('%B')
    data = organic_seasonal.loc[month_num]
    print(f'{month_name}: Revenue=${data["Revenue_Clean"]:,.0f}, Orders={data["Last Click Orders"]:.0f}, Conv Rate={data["Conversion_Rate"]:.2f}%')

print('\nCHANNEL EFFICIENCY COMPARISON')
print('=' * 40)

# Calculate efficiency metrics
channel_efficiency = paid_df.groupby('Channel').agg({
    'ROAS': 'mean',
    'Cost_Per_Order': 'mean',
    'Conversion_Rate': 'mean',
    'Spend_Clean': 'sum',
    'Revenue_Clean': 'sum'
}).round(2)

print('Channel Performance Ranking by ROAS:')
ranked_by_roas = channel_efficiency.sort_values('ROAS', ascending=False)
for i, (channel, data) in enumerate(ranked_by_roas.iterrows(), 1):
    print(f'{i}. {channel}: ROAS {data["ROAS"]}, Cost/Order ${data["Cost_Per_Order"]:,.0f}, Conv Rate {data["Conversion_Rate"]:.3f}%')

print('\nFINANCIAL IMPACT CALCULATIONS')
print('=' * 40)

# Calculate potential budget reallocation impact
google_ads_data = channel_efficiency.loc['Google Ads']
youtube_ads_data = channel_efficiency.loc['YouTube Ads']
fb_ads_data = channel_efficiency.loc['FB Ads']

print(f'YouTube Ads Total Spend: ${youtube_ads_data["Spend_Clean"]:,.0f}')
print(f'YouTube Ads ROAS: {youtube_ads_data["ROAS"]:.2f}')
print(f'Google Ads ROAS: {google_ads_data["ROAS"]:.2f}')

# If we moved YouTube Ads budget to Google Ads
youtube_to_google_impact = youtube_ads_data["Spend_Clean"] * (google_ads_data["ROAS"] - youtube_ads_data["ROAS"])
print(f'Potential additional revenue from moving YouTube budget to Google Ads: ${youtube_to_google_impact:,.0f}')

print(f'\nFB Ads Total Spend: ${fb_ads_data["Spend_Clean"]:,.0f}')
print(f'FB Ads ROAS: {fb_ads_data["ROAS"]:.2f}')
fb_to_google_impact = fb_ads_data["Spend_Clean"] * (google_ads_data["ROAS"] - fb_ads_data["ROAS"])
print(f'Potential additional revenue from moving FB budget to Google Ads: ${fb_to_google_impact:,.0f}')

print('\nEMAIL OPTIMIZATION OPPORTUNITIES')
print('=' * 40)

# Email capture analysis
email_df = df[df['Channel'].isin(['Google Ads', 'YouTube Ads', 'FB Ads'])].copy()
email_perf = email_df.groupby('Channel').agg({
    'Last Click Email Captures': 'sum',
    'Email capture conversions 30 day window': 'sum',
    'Email capture conversions 60 day window': 'sum',
    'Visitors': 'sum'
}).round(0)

email_perf['Email_Capture_Rate'] = (email_perf['Last Click Email Captures'] / email_perf['Visitors'] * 100).round(2)
email_perf['Email_30d_Conv_Rate'] = (email_perf['Email capture conversions 30 day window'] / email_perf['Last Click Email Captures'] * 100).round(2)

print('Email Performance by Channel:')
for channel in email_perf.index:
    data = email_perf.loc[channel]
    print(f'{channel}:')
    print(f'  Email Capture Rate: {data["Email_Capture_Rate"]:.2f}%')
    print(f'  Email 30d Conversion Rate: {data["Email_30d_Conv_Rate"]:.2f}%')
    print(f'  Total Email Captures: {data["Last Click Email Captures"]:,.0f}')
    
# Calculate opportunity if all channels matched Google Ads email capture rate
google_email_rate = email_perf.loc['Google Ads', 'Email_Capture_Rate']
for channel in ['YouTube Ads', 'FB Ads']:
    current_rate = email_perf.loc[channel, 'Email_Capture_Rate']
    visitors = email_perf.loc[channel, 'Visitors']
    current_captures = email_perf.loc[channel, 'Last Click Email Captures']
    potential_captures = visitors * (google_email_rate / 100)
    additional_captures = potential_captures - current_captures
    
    # Estimate revenue impact using Google Ads email conversion rate
    google_email_conv = email_perf.loc['Google Ads', 'Email_30d_Conv_Rate'] / 100
    additional_orders = additional_captures * google_email_conv
    avg_order_value = 4500  # Estimated based on revenue/orders ratio
    additional_revenue = additional_orders * avg_order_value
    
    print(f'\n{channel} Email Optimization Opportunity:')
    print(f'  Current capture rate: {current_rate:.2f}%')
    print(f'  Target capture rate: {google_email_rate:.2f}%')
    print(f'  Additional email captures: {additional_captures:,.0f}')
    print(f'  Estimated additional revenue: ${additional_revenue:,.0f}')