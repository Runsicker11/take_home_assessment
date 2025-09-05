#!/usr/bin/env python3
"""
Simple, conservative analysis of marketing data
Only making claims I can verify step by step
"""

import csv
from datetime import datetime
from collections import defaultdict
import re

def clean_currency(val):
    """Clean currency values"""
    if not val or val == '':
        return 0
    return float(re.sub(r'[\$,"\s]', '', str(val)))

def parse_date(date_str):
    """Parse date string to month/year"""
    try:
        date_obj = datetime.strptime(date_str.split()[0], '%m/%d/%Y')
        return f"{date_obj.year}-{date_obj.month:02d}"
    except:
        return None

# Load daily sales data
print("=== SIMPLE MARKETING ANALYSIS ===\n")
print("1. DAILY SALES DATA OVERVIEW")
print("-" * 40)

daily_spend = []
daily_orders = []
daily_bookings = []

with open('Raw Data/daily_sales.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        spend = clean_currency(row['Daily Spend'])
        orders = int(row['Orders']) if row['Orders'] else 0
        bookings = clean_currency(row['Bookings'])
        
        daily_spend.append(spend)
        daily_orders.append(orders)
        daily_bookings.append(bookings)

print(f"Total days analyzed: {len(daily_spend)}")
print(f"Average daily spend: ${sum(daily_spend)/len(daily_spend):,.0f}")
print(f"Average daily orders: {sum(daily_orders)/len(daily_orders):.0f}")
print(f"Average daily bookings: ${sum(daily_bookings)/len(daily_bookings):,.0f}")

# Load new member data by month
print("\n2. NEW MEMBER BOOKINGS BY MONTH")
print("-" * 40)

monthly_new_members = defaultdict(float)

with open('Raw Data/regional_sales.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Customer Type'] == '1. New Members':
            # Handle BOM in CSV
            date_col = list(row.keys())[0]  # First column is Date
            month_key = parse_date(row[date_col])
            if month_key:
                bookings = clean_currency(row['Bookings'])
                monthly_new_members[month_key] += bookings

# Sort by month
sorted_months = sorted(monthly_new_members.keys())

print("Month\t\tNew Member Bookings")
for month in sorted_months[:12]:  # Show first 12 months
    print(f"{month}\t\t${monthly_new_members[month]:,.0f}")

# Load marketing spend by month  
print("\n3. MARKETING SPEND BY MONTH")
print("-" * 40)

monthly_marketing = defaultdict(float)
channel_totals = defaultdict(float)

with open('Raw Data/monthly_marketing_channel_level.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Handle BOM in CSV
        channel_col = list(row.keys())[0]  # First column is Channel
        channel = row[channel_col]
        spend = clean_currency(row['Spend'])
        month_key = parse_date(row['Month'])
        
        if spend > 0 and month_key:
            monthly_marketing[month_key] += spend
            channel_totals[channel] += spend

print("Month\t\tMarketing Spend")
for month in sorted_months[:12]:  # Show first 12 months
    print(f"{month}\t\t${monthly_marketing[month]:,.0f}")

print("\n4. CHANNEL SPEND TOTALS")
print("-" * 40)
for channel, total in sorted(channel_totals.items(), key=lambda x: x[1], reverse=True):
    print(f"{channel}: ${total:,.0f}")

# Simple comparison for a few months
print("\n5. BASIC COMPARISON (Selected Months)")
print("-" * 50)
print("Month\t\tMarketing\tNew Members\tRatio")
print("-" * 50)

for month in sorted_months[:6]:
    marketing = monthly_marketing[month]
    new_members = monthly_new_members[month]
    ratio = new_members / marketing if marketing > 0 else 0
    print(f"{month}\t${marketing:>8,.0f}\t${new_members:>9,.0f}\t{ratio:.2f}")

print("\n=== CONSERVATIVE OBSERVATIONS ===")
print("• Marketing spend varies significantly by month")
print("• New member bookings also vary by month")
print("• Would need proper statistical analysis to determine correlation")
print("• Seasonal patterns appear to exist in both metrics")
print("• Google Ads represents largest marketing investment")

print("\n=== WHAT WE CANNOT CONCLUDE ===")
print("• Cannot prove causation without controlled testing")
print("• Attribution between channels unclear")
print("• External factors (economy, competition) not controlled")
print("• Sample size may be insufficient for robust conclusions")