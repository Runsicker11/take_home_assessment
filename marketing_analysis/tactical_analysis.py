import pandas as pd
import numpy as np

# Read the CSV file
df = pd.read_csv('Raw Data/monthly_marketing_channel_level.csv')

# Clean the data
df['Spend_Clean'] = df['Spend'].str.replace('$', '').str.replace(',', '').str.replace(' ', '')
df['Spend_Clean'] = pd.to_numeric(df['Spend_Clean'], errors='coerce')
df['Revenue_Clean'] = pd.to_numeric(df['Last Click Revenue'], errors='coerce')
df['Month'] = pd.to_datetime(df['Month'])
df['ROAS'] = df['Revenue_Clean'] / df['Spend_Clean']

print('TACTICAL OPPORTUNITIES ANALYSIS')
print('=' * 50)

# Identify underperforming months that could be fixed
paid_df = df[df['Channel'].isin(['Google Ads', 'YouTube Ads', 'FB Ads'])].copy()

print('\nUNDERPERFORMING INSTANCES TO INVESTIGATE')
print('=' * 50)

# Find instances where ROAS is significantly below channel average
for channel in ['Google Ads', 'YouTube Ads', 'FB Ads']:
    channel_data = paid_df[paid_df['Channel'] == channel].copy()
    avg_roas = channel_data['ROAS'].mean()
    threshold = avg_roas * 0.7  # 30% below average
    
    underperforming = channel_data[channel_data['ROAS'] < threshold].copy()
    
    if len(underperforming) > 0:
        print(f'\n{channel} - Avg ROAS: {avg_roas:.2f}')
        print('Underperforming months (30%+ below average):')
        for _, row in underperforming.iterrows():
            month_str = row['Month'].strftime('%Y-%m')
            print(f'  {month_str}: ROAS {row["ROAS"]:.2f}, Spend ${row["Spend_Clean"]:,.0f}, Revenue ${row["Revenue_Clean"]:,.0f}')

print('\nHIGH SPEND / LOW PERFORMANCE MONTHS')
print('=' * 45)

# Find high spend months with poor performance
high_spend_threshold = paid_df['Spend_Clean'].quantile(0.75)  # Top 25% spend
low_roas_threshold = paid_df['ROAS'].quantile(0.25)  # Bottom 25% ROAS

problematic = paid_df[(paid_df['Spend_Clean'] > high_spend_threshold) & 
                     (paid_df['ROAS'] < low_roas_threshold)].copy()

if len(problematic) > 0:
    print('High spend + Low ROAS combinations:')
    for _, row in problematic.iterrows():
        month_str = row['Month'].strftime('%Y-%m')
        print(f'{row["Channel"]} {month_str}: Spend ${row["Spend_Clean"]:,.0f}, ROAS {row["ROAS"]:.2f}')

print('\nCONVERSION RATE OPPORTUNITIES')
print('=' * 35)

# Find channels/months with low conversion rates but high traffic
for channel in ['Google Ads', 'YouTube Ads', 'FB Ads']:
    channel_data = paid_df[paid_df['Channel'] == channel].copy()
    channel_data['Conversion_Rate'] = (channel_data['Last Click Orders'] / channel_data['Visitors']) * 100
    
    avg_conv_rate = channel_data['Conversion_Rate'].mean()
    high_traffic_threshold = channel_data['Visitors'].quantile(0.75)
    
    opportunities = channel_data[
        (channel_data['Visitors'] > high_traffic_threshold) & 
        (channel_data['Conversion_Rate'] < avg_conv_rate * 0.8)
    ].copy()
    
    if len(opportunities) > 0:
        print(f'\n{channel} - Avg Conv Rate: {avg_conv_rate:.3f}%')
        print('High traffic + Low conversion opportunities:')
        for _, row in opportunities.iterrows():
            month_str = row['Month'].strftime('%Y-%m')
            potential_orders = row['Visitors'] * (avg_conv_rate / 100)
            current_orders = row['Last Click Orders']
            missed_orders = potential_orders - current_orders
            avg_order_value = row['Revenue_Clean'] / row['Last Click Orders'] if row['Last Click Orders'] > 0 else 0
            missed_revenue = missed_orders * avg_order_value
            
            print(f'  {month_str}: {row["Visitors"]:,.0f} visitors, {row["Conversion_Rate"]:.3f}% conv rate')
            print(f'    Potential missed orders: {missed_orders:.0f}, Missed revenue: ${missed_revenue:,.0f}')

print('\nQUICK WIN BUDGET REALLOCATION')
print('=' * 40)

# Calculate monthly budget efficiency
monthly_efficiency = paid_df.groupby([paid_df['Month'].dt.strftime('%Y-%m'), 'Channel']).agg({
    'ROAS': 'first',
    'Spend_Clean': 'first'
}).reset_index()

# For recent months, identify reallocation opportunities
recent_months = ['2025-04', '2025-05', '2025-06']
for month in recent_months:
    month_data = monthly_efficiency[monthly_efficiency['Month'] == month].copy()
    if len(month_data) > 1:
        best_channel = month_data.loc[month_data['ROAS'].idxmax()]
        worst_channel = month_data.loc[month_data['ROAS'].idxmin()]
        
        if best_channel['ROAS'] > worst_channel['ROAS'] * 1.5:  # 50%+ better
            reallocation_amount = worst_channel['Spend_Clean'] * 0.3  # Move 30%
            additional_revenue = reallocation_amount * (best_channel['ROAS'] - worst_channel['ROAS'])
            
            print(f'\n{month} Reallocation Opportunity:')
            print(f'  Move ${reallocation_amount:,.0f} from {worst_channel["Channel"]} (ROAS: {worst_channel["ROAS"]:.2f})')
            print(f'  To {best_channel["Channel"]} (ROAS: {best_channel["ROAS"]:.2f})')
            print(f'  Estimated additional revenue: ${additional_revenue:,.0f}')

print('\nSEASONAL BUDGET PLANNING')
print('=' * 30)

# Identify best and worst performing months
organic_data = df[df['Channel'] == 'Organic + Direct'].copy()
organic_monthly = organic_data.groupby(organic_data['Month'].dt.month).agg({
    'Revenue_Clean': 'mean',
    'Last Click Orders': 'mean'
}).round(0)

print('Organic traffic patterns (monthly averages):')
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

best_months = []
for month_num in range(1, 13):
    if month_num in organic_monthly.index:
        revenue = organic_monthly.loc[month_num, 'Revenue_Clean']
        orders = organic_monthly.loc[month_num, 'Last Click Orders']
        print(f'{months[month_num-1]}: ${revenue:,.0f} revenue, {orders:.0f} orders')
        
        if revenue > organic_monthly['Revenue_Clean'].mean() * 1.2:
            best_months.append(months[month_num-1])

print(f'\nBest performing months for budget increases: {", ".join(best_months)}')

# Calculate paid channel seasonal performance
paid_seasonal = paid_df.groupby([paid_df['Month'].dt.month, 'Channel']).agg({
    'ROAS': 'mean',
    'Spend_Clean': 'mean'
}).round(2)

print('\nPaid channel seasonal ROAS patterns:')
for channel in ['Google Ads', 'YouTube Ads', 'FB Ads']:
    channel_seasonal = paid_seasonal.xs(channel, level=1)
    if len(channel_seasonal) > 0:
        best_month_num = channel_seasonal['ROAS'].idxmax()
        worst_month_num = channel_seasonal['ROAS'].idxmin()
        best_roas = channel_seasonal.loc[best_month_num, 'ROAS']
        worst_roas = channel_seasonal.loc[worst_month_num, 'ROAS']
        
        print(f'{channel}: Best {months[best_month_num-1]} ({best_roas}), Worst {months[worst_month_num-1]} ({worst_roas})')