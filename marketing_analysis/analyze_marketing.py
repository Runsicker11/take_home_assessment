import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('Raw Data/monthly_marketing_channel_level.csv')

# Clean the data
df['Spend_Clean'] = df['Spend'].str.replace('$', '').str.replace(',', '').str.replace(' ', '')
df['Spend_Clean'] = pd.to_numeric(df['Spend_Clean'], errors='coerce')
df['Revenue_Clean'] = pd.to_numeric(df['Last Click Revenue'], errors='coerce')

# Convert Month to datetime
df['Month'] = pd.to_datetime(df['Month'])

# Calculate key metrics
df['ROAS'] = df['Revenue_Clean'] / df['Spend_Clean']
df['Cost_Per_Order'] = df['Spend_Clean'] / df['Last Click Orders']
df['Conversion_Rate'] = (df['Last Click Orders'] / df['Visitors']) * 100
df['Cost_Per_Visitor'] = df['Spend_Clean'] / df['Visitors']
df['Email_Capture_Rate'] = (df['Last Click Email Captures'] / df['Visitors']) * 100
df['Email_30d_Conv_Rate'] = (df['Email capture conversions 30 day window'] / df['Last Click Email Captures']) * 100
df['Email_60d_Conv_Rate'] = (df['Email capture conversions 60 day window'] / df['Last Click Email Captures']) * 100

# Display summary by channel
print('CHANNEL PERFORMANCE SUMMARY')
print('=' * 50)

channels = ['Google Ads', 'YouTube Ads', 'FB Ads']
for channel in channels:
    if channel not in df['Channel'].values:
        continue
    channel_data = df[df['Channel'] == channel].copy()
    
    print(f'\n{channel.upper()}')
    print(f'Total Spend: ${channel_data["Spend_Clean"].sum():,.0f}')
    print(f'Total Revenue: ${channel_data["Revenue_Clean"].sum():,.0f}')
    print(f'Total Orders: {channel_data["Last Click Orders"].sum():,.0f}')
    print(f'Average ROAS: {channel_data["ROAS"].mean():.2f}')
    print(f'Average Cost per Order: ${channel_data["Cost_Per_Order"].mean():.0f}')
    print(f'Average Conversion Rate: {channel_data["Conversion_Rate"].mean():.2f}%')
    print(f'Average Email Capture Rate: {channel_data["Email_Capture_Rate"].mean():.2f}%')
    print(f'Average Email 30d Conv Rate: {channel_data["Email_30d_Conv_Rate"].mean():.2f}%')

# Organic + Direct summary
organic_data = df[df['Channel'] == 'Organic + Direct'].copy()
print(f'\nORGANIC + DIRECT')
print(f'Total Revenue: ${organic_data["Revenue_Clean"].sum():,.0f}')
print(f'Total Orders: {organic_data["Last Click Orders"].sum():,.0f}')
print(f'Average Conversion Rate: {organic_data["Conversion_Rate"].mean():.2f}%')
print(f'Average Email Capture Rate: {organic_data["Email_Capture_Rate"].mean():.2f}%')

print('\n\nMONTHLY TRENDS BY CHANNEL')
print('=' * 50)

# Monthly analysis
monthly_summary = df.groupby(['Channel', df['Month'].dt.strftime('%Y-%m')]).agg({
    'Spend_Clean': 'sum',
    'Revenue_Clean': 'sum',
    'Last Click Orders': 'sum',
    'ROAS': 'mean',
    'Conversion_Rate': 'mean'
}).round(2)

print(monthly_summary)

print('\n\nTOP PERFORMING MONTHS BY ROAS')
print('=' * 40)
paid_channels = df[df['Channel'].isin(['Google Ads', 'YouTube Ads', 'FB Ads'])].copy()
top_roas = paid_channels.nlargest(10, 'ROAS')[['Channel', 'Month', 'ROAS', 'Spend_Clean', 'Revenue_Clean', 'Last Click Orders']]
print(top_roas.to_string(index=False))

print('\n\nWORST PERFORMING MONTHS BY ROAS')
print('=' * 40)
worst_roas = paid_channels.nsmallest(10, 'ROAS')[['Channel', 'Month', 'ROAS', 'Spend_Clean', 'Revenue_Clean', 'Last Click Orders']]
print(worst_roas.to_string(index=False))

print('\n\nEMAIL CAPTURE ANALYSIS')
print('=' * 30)
email_analysis = df[df['Channel'].isin(['Google Ads', 'YouTube Ads', 'FB Ads'])].groupby('Channel').agg({
    'Email_Capture_Rate': 'mean',
    'Email_30d_Conv_Rate': 'mean',
    'Email_60d_Conv_Rate': 'mean',
    'Last Click Email Captures': 'sum'
}).round(2)
print(email_analysis)