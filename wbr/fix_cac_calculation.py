#!/usr/bin/env python3
"""
Fix CAC Calculation - Only Count New Members
"""

import pandas as pd
import json
from datetime import datetime

def calculate_new_customers_only():
    # Load regional sales data
    regional_df = pd.read_csv('C:/Users/eunhe/Documents/eight_sleep_assessment/Raw Data/regional_sales.csv')
    
    # Convert Date column to datetime
    regional_df['Date'] = pd.to_datetime(regional_df['Date'])
    
    # Clean Orders column (remove quotes and spaces)
    regional_df['Orders'] = regional_df['Orders'].astype(str).str.replace('"', '').str.replace(',', '').str.replace(' ', '').astype(int)
    
    print("=== CAC CALCULATION FIX ===")
    print("Filtering for ONLY '1. New Members' (not all order types)\n")
    
    # Filter for only new members
    new_members_df = regional_df[regional_df['Customer Type'] == '1. New Members'].copy()
    
    # Current week: July 7-13, 2025
    current_week_start = pd.to_datetime('2025-07-07')
    current_week_end = pd.to_datetime('2025-07-13')
    
    current_week_new = new_members_df[
        (new_members_df['Date'] >= current_week_start) & 
        (new_members_df['Date'] <= current_week_end)
    ]
    
    # Previous week: June 30 - July 6, 2025  
    previous_week_start = pd.to_datetime('2025-06-30')
    previous_week_end = pd.to_datetime('2025-07-06')
    
    previous_week_new = new_members_df[
        (new_members_df['Date'] >= previous_week_start) & 
        (new_members_df['Date'] <= previous_week_end)
    ]
    
    # Calculate new customer orders
    current_week_new_orders = current_week_new['Orders'].sum()
    previous_week_new_orders = previous_week_new['Orders'].sum()
    
    print(f"CURRENT WEEK (July 7-13): New Customer Orders = {current_week_new_orders}")
    print(f"PREVIOUS WEEK (June 30-July 6): New Customer Orders = {previous_week_new_orders}")
    
    # Load existing spend data for CAC calculation
    daily_df = pd.read_csv('C:/Users/eunhe/Documents/eight_sleep_assessment/Raw Data/daily_sales.csv')
    daily_df['Date'] = pd.to_datetime(daily_df['Date'])
    
    # Current week spend
    current_week_daily = daily_df[
        (daily_df['Date'] >= current_week_start) & 
        (daily_df['Date'] <= current_week_end)
    ]
    
    previous_week_daily = daily_df[
        (daily_df['Date'] >= previous_week_start) & 
        (daily_df['Date'] <= previous_week_end)
    ]
    
    # Clean spend data
    def clean_currency(val):
        if pd.isna(val):
            return 0
        return float(str(val).replace('$', '').replace(',', '').replace('"', '').replace(' ', ''))
    
    current_week_daily['Daily Spend'] = current_week_daily['Daily Spend'].apply(clean_currency)
    previous_week_daily['Daily Spend'] = previous_week_daily['Daily Spend'].apply(clean_currency)
    
    current_week_spend = current_week_daily['Daily Spend'].sum()
    previous_week_spend = previous_week_daily['Daily Spend'].sum()
    
    print(f"\nCURRENT WEEK SPEND: ${current_week_spend:,.2f}")
    print(f"PREVIOUS WEEK SPEND: ${previous_week_spend:,.2f}")
    
    # Calculate corrected CAC
    current_week_cac = current_week_spend / current_week_new_orders if current_week_new_orders > 0 else 0
    previous_week_cac = previous_week_spend / previous_week_new_orders if previous_week_new_orders > 0 else 0
    
    print(f"\n=== CORRECTED CAC CALCULATION ===")
    print(f"CURRENT WEEK CAC: ${current_week_cac:.2f} (${current_week_spend:,.0f} ÷ {current_week_new_orders} new customers)")
    print(f"PREVIOUS WEEK CAC: ${previous_week_cac:.2f} (${previous_week_spend:,.0f} ÷ {previous_week_new_orders} new customers)")
    
    # Compare with incorrect calculation
    print(f"\n=== COMPARISON WITH CURRENT (INCORRECT) CALCULATION ===")
    
    # Get total orders from all customer types for comparison
    current_week_all_orders = regional_df[
        (regional_df['Date'] >= current_week_start) & 
        (regional_df['Date'] <= current_week_end)
    ]['Orders'].sum()
    
    incorrect_cac = current_week_spend / current_week_all_orders if current_week_all_orders > 0 else 0
    
    print(f"INCORRECT CAC (using ALL orders): ${incorrect_cac:.2f} (${current_week_spend:,.0f} ÷ {current_week_all_orders} total orders)")
    print(f"CORRECT CAC (new members only): ${current_week_cac:.2f} (${current_week_spend:,.0f} ÷ {current_week_new_orders} new customers)")
    print(f"DIFFERENCE: ${current_week_cac - incorrect_cac:.2f} ({((current_week_cac - incorrect_cac) / incorrect_cac * 100):.1f}% higher)")
    
    return {
        'current_week_new_orders': current_week_new_orders,
        'previous_week_new_orders': previous_week_new_orders,
        'current_week_cac': current_week_cac,
        'previous_week_cac': previous_week_cac,
        'current_week_spend': current_week_spend,
        'previous_week_spend': previous_week_spend
    }

if __name__ == "__main__":
    results = calculate_new_customers_only()