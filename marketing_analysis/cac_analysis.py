"""
CAC (Customer Acquisition Cost) Analysis for Eight Sleep
Assumes orders with AOV > $3,000 are new customers
"""

import pandas as pd
import numpy as np

def clean_monetary_value(val):
    """Clean monetary values"""
    if pd.isna(val) or val == '':
        return 0
    if isinstance(val, str):
        return float(val.replace('$', '').replace(',', '').strip())
    return float(val)

def analyze_cac():
    # Load data
    df = pd.read_csv('Raw Data/monthly_marketing_channel_level.csv')
    
    # Clean data
    df['Spend'] = df['Spend'].apply(clean_monetary_value)
    df['Last Click Revenue'] = df['Last Click Revenue'].apply(clean_monetary_value)
    df['Month'] = pd.to_datetime(df['Month'], format='%m/%d/%Y %H:%M')
    df['Last Click Orders'] = pd.to_numeric(df['Last Click Orders'], errors='coerce').fillna(0).astype(int)
    
    # Calculate AOV
    df['AOV'] = np.where(df['Last Click Orders'] > 0, 
                         df['Last Click Revenue'] / df['Last Click Orders'], 0)
    
    # Identify new customers (AOV > $3,000)
    df['New Customers'] = np.where(df['AOV'] > 3000, df['Last Click Orders'], 0)
    
    # For channels with lower AOV, estimate new customers based on proportion
    # Assumption: In high AOV channels, most are new; in low AOV, estimate based on revenue
    df['Estimated New Customers'] = np.where(
        df['AOV'] > 3000,
        df['Last Click Orders'],  # All orders are new customers
        np.where(
            df['AOV'] > 1000,
            df['Last Click Orders'] * 0.5,  # Mixed - assume 50% new
            df['Last Click Orders'] * 0.1   # Low AOV - mostly renewals/accessories
        )
    )
    
    # Calculate CAC by channel
    channel_cac = df.groupby('Channel').agg({
        'Spend': 'sum',
        'Last Click Orders': 'sum',
        'Last Click Revenue': 'sum',
        'Estimated New Customers': 'sum'
    })
    
    channel_cac['AOV'] = channel_cac['Last Click Revenue'] / channel_cac['Last Click Orders']
    channel_cac['CAC'] = channel_cac['Spend'] / channel_cac['Estimated New Customers'].replace(0, np.nan)
    
    print("="*60)
    print("CAC ANALYSIS BY CHANNEL")
    print("="*60)
    print("\nChannel Performance:")
    for channel in channel_cac.index:
        if channel != 'Organic + Direct':  # Skip organic for CAC
            spend = channel_cac.loc[channel, 'Spend']
            new_custs = channel_cac.loc[channel, 'Estimated New Customers']
            cac = channel_cac.loc[channel, 'CAC']
            aov = channel_cac.loc[channel, 'AOV']
            print(f"\n{channel}:")
            print(f"  Total Spend: ${spend:,.0f}")
            print(f"  Est. New Customers: {new_custs:.0f}")
            print(f"  CAC: ${cac:,.0f}")
            print(f"  AOV: ${aov:,.0f}")
    
    # Monthly CAC trend
    monthly_cac = df.groupby('Month').agg({
        'Spend': 'sum',
        'Estimated New Customers': 'sum',
        'Last Click Revenue': 'sum'
    })
    
    monthly_cac['CAC'] = monthly_cac['Spend'] / monthly_cac['Estimated New Customers'].replace(0, np.nan)
    
    print("\n" + "="*60)
    print("MONTHLY CAC TREND")
    print("="*60)
    
    for month in monthly_cac.index:
        cac = monthly_cac.loc[month, 'CAC']
        new_custs = monthly_cac.loc[month, 'Estimated New Customers']
        if not np.isnan(cac):
            print(f"{month.strftime('%Y-%m')}: CAC = ${cac:,.0f} ({new_custs:.0f} new customers)")
    
    # Overall metrics
    total_spend = df['Spend'].sum()
    total_new_customers = df['Estimated New Customers'].sum()
    overall_cac = total_spend / total_new_customers if total_new_customers > 0 else 0
    
    print("\n" + "="*60)
    print("OVERALL METRICS")
    print("="*60)
    print(f"Total Marketing Spend: ${total_spend:,.0f}")
    print(f"Estimated New Customers: {total_new_customers:.0f}")
    print(f"Overall Blended CAC: ${overall_cac:,.0f}")
    
    return df, channel_cac, monthly_cac

if __name__ == "__main__":
    analyze_cac()