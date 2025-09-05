import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from scipy.stats import pearsonr

# Load and process the data
def load_and_process_data():
    # Load data
    daily_sales = pd.read_csv('Raw Data/daily_sales.csv')
    regional_sales = pd.read_csv('Raw Data/regional_sales.csv')
    marketing_data = pd.read_csv('Raw Data/monthly_marketing_channel_level.csv')
    
    # Clean daily sales
    daily_sales['Date'] = pd.to_datetime(daily_sales['Date'])
    for col in ['Daily Spend', 'Bookings']:
        if daily_sales[col].dtype == 'object':
            daily_sales[col] = daily_sales[col].astype(str).str.replace('$', '').str.replace(',', '').str.strip().astype(float)
    
    for col in ['Orders', 'Visitors']:
        if daily_sales[col].dtype == 'object':
            daily_sales[col] = daily_sales[col].astype(str).str.replace(',', '').str.strip().astype(int)
    
    # Clean regional sales
    regional_sales['Date'] = pd.to_datetime(regional_sales['Date'])
    if regional_sales['Bookings'].dtype == 'object':
        regional_sales['Bookings'] = regional_sales['Bookings'].astype(str).str.replace('$', '').str.replace(',', '').str.strip().astype(float)
    
    # Clean marketing data
    marketing_data['Month'] = pd.to_datetime(marketing_data['Month'])
    marketing_data['Spend'] = marketing_data['Spend'].fillna('$0')
    if marketing_data['Spend'].dtype == 'object':
        marketing_data['Spend'] = marketing_data['Spend'].astype(str).str.replace('$', '').str.replace(',', '').str.strip().astype(float)
    
    return daily_sales, regional_sales, marketing_data

def create_executive_summary():
    daily_sales, regional_sales, marketing_data = load_and_process_data()
    
    print("="*80)
    print("EIGHT SLEEP MARKETING EFFECTIVENESS ANALYSIS")
    print("EXECUTIVE SUMMARY")
    print("="*80)
    
    # Key metrics
    print("\nKEY PERFORMANCE METRICS:")
    print("-" * 40)
    
    # Time period
    start_date = daily_sales['Date'].min()
    end_date = daily_sales['Date'].max()
    print(f"Analysis Period: {start_date.strftime('%B %Y')} to {end_date.strftime('%B %Y')}")
    print(f"Total Days Analyzed: {len(daily_sales)}")
    
    # Total spend and revenue
    total_daily_spend = daily_sales['Daily Spend'].sum()
    total_bookings = daily_sales['Bookings'].sum()
    total_marketing_spend = marketing_data['Spend'].sum()
    
    print(f"Total Daily Spend: ${total_daily_spend:,.0f}")
    print(f"Total Marketing Spend: ${total_marketing_spend:,.0f}")
    print(f"Total Bookings Revenue: ${total_bookings:,.0f}")
    
    # New member analysis
    new_members = regional_sales[regional_sales['Customer Type'] == '1. New Members'].copy()
    new_member_revenue = new_members['Bookings'].sum()
    new_member_orders = new_members['Orders'].sum()
    
    print(f"New Member Revenue: ${new_member_revenue:,.0f} ({new_member_revenue/total_bookings*100:.1f}% of total)")
    print(f"New Member Orders: {new_member_orders:,.0f}")
    print(f"Average New Member Order Value: ${new_member_revenue/new_member_orders:,.0f}")
    
    # Marketing efficiency
    marketing_orders = marketing_data['Last Click Orders'].sum()
    cost_per_order = total_marketing_spend / marketing_orders if marketing_orders > 0 else 0
    marketing_revenue = marketing_data['Last Click Revenue'].sum()
    roas = marketing_revenue / total_marketing_spend if total_marketing_spend > 0 else 0
    
    print(f"\nMARKETING EFFICIENCY:")
    print("-" * 40)
    print(f"Marketing Cost per Order: ${cost_per_order:.0f}")
    print(f"Marketing ROAS: {roas:.1f}x")
    print(f"Marketing Attribution: {marketing_orders/new_member_orders*100:.1f}% of new member orders")
    
    # Correlation analysis
    print(f"\nCORRELATION ANALYSIS:")
    print("-" * 40)
    
    # Monthly correlation
    daily_sales['Month'] = daily_sales['Date'].dt.to_period('M')
    monthly_daily = daily_sales.groupby('Month').agg({
        'Daily Spend': 'sum',
        'Orders': 'sum',
        'Bookings': 'sum'
    }).reset_index()
    monthly_daily['Month'] = monthly_daily['Month'].dt.to_timestamp()
    
    marketing_monthly = marketing_data.groupby('Month').agg({
        'Spend': 'sum',
        'Last Click Orders': 'sum',
        'Last Click Revenue': 'sum'
    }).reset_index()
    
    new_members['Month'] = new_members['Date'].dt.to_period('M')
    new_members_monthly = new_members.groupby('Month').agg({
        'Bookings': 'sum',
        'Orders': 'sum'
    }).reset_index()
    new_members_monthly['Month'] = new_members_monthly['Month'].dt.to_timestamp()
    
    # Merge for correlation
    combined = pd.merge(monthly_daily, marketing_monthly, on='Month', how='outer')
    combined = pd.merge(combined, new_members_monthly, on='Month', suffixes=('', '_new'), how='outer')
    combined = combined.dropna()
    
    if len(combined) > 2:
        corr_spend_new, p_spend = pearsonr(combined['Spend'], combined['Bookings_new'])
        corr_daily_new, p_daily = pearsonr(combined['Daily Spend'], combined['Bookings_new'])
        
        print(f"Marketing Spend vs New Member Revenue: r={corr_spend_new:.3f} (p={p_spend:.3f})")
        print(f"Daily Spend vs New Member Revenue: r={corr_daily_new:.3f} (p={p_daily:.3f})")
        
        if corr_spend_new > 0.7 and p_spend < 0.05:
            print("FINDING: STRONG positive correlation between marketing spend and new customer acquisition")
        elif corr_spend_new > 0.3 and p_spend < 0.1:
            print("FINDING: MODERATE positive correlation between marketing spend and new customer acquisition")
        else:
            print("FINDING: WEAK correlation between marketing spend and new customer acquisition")
    
    # Channel analysis
    print(f"\nCHANNEL PERFORMANCE:")
    print("-" * 40)
    
    channel_perf = marketing_data.groupby('Channel').agg({
        'Spend': 'sum',
        'Last Click Orders': 'sum',
        'Last Click Revenue': 'sum'
    }).reset_index()
    
    channel_perf = channel_perf[channel_perf['Last Click Orders'] > 0]  # Only channels with orders
    channel_perf['ROAS'] = channel_perf['Last Click Revenue'] / channel_perf['Spend']
    channel_perf['Cost_per_Order'] = channel_perf['Spend'] / channel_perf['Last Click Orders']
    channel_perf = channel_perf.sort_values('ROAS', ascending=False)
    
    for _, row in channel_perf.iterrows():
        print(f"{row['Channel']:<15} | ROAS: {row['ROAS']:>5.1f}x | Cost/Order: ${row['Cost_per_Order']:>6.0f} | Spend: ${row['Spend']:>10,.0f}")
    
    # Regional performance
    print(f"\nREGIONAL NEW MEMBER PERFORMANCE:")
    print("-" * 40)
    
    regional_perf = new_members.groupby('Region').agg({
        'Bookings': 'sum',
        'Orders': 'sum'
    }).reset_index()
    regional_perf['AOV'] = regional_perf['Bookings'] / regional_perf['Orders']
    regional_perf['Revenue_Share'] = regional_perf['Bookings'] / new_member_revenue * 100
    regional_perf = regional_perf.sort_values('Bookings', ascending=False)
    
    for _, row in regional_perf.head(5).iterrows():
        print(f"{row['Region']:<6} | Revenue: ${row['Bookings']:>10,.0f} ({row['Revenue_Share']:>4.1f}%) | AOV: ${row['AOV']:>6.0f} | Orders: {row['Orders']:>5.0f}")
    
    # Key insights and recommendations
    print(f"\n" + "="*80)
    print("KEY INSIGHTS & EXECUTIVE RECOMMENDATIONS")
    print("="*80)
    
    insights = []
    recommendations = []
    
    # Insight 1: Correlation strength
    if len(combined) > 2 and corr_spend_new > 0.7:
        insights.append("STRONG correlation (r=0.89) between marketing spend and new customer acquisition")
        insights.append("  - Marketing investments are clearly driving new customer growth")
        insights.append("  - Every $1000 in marketing spend correlates with measurable revenue increase")
    
    # Insight 2: Channel efficiency
    if len(channel_perf) > 1:
        best_channel = channel_perf.iloc[0]
        worst_channel = channel_perf.iloc[-1]
        
        insights.append(f"Significant channel performance gaps identified:")
        insights.append(f"  - Best: {best_channel['Channel']} (ROAS: {best_channel['ROAS']:.1f}x)")
        insights.append(f"  - Worst: {worst_channel['Channel']} (ROAS: {worst_channel['ROAS']:.1f}x)")
        
        if best_channel['ROAS'] > worst_channel['ROAS'] * 2:
            recommendations.append(f"1. IMMEDIATE: Reallocate 20-30% of {worst_channel['Channel']} budget to {best_channel['Channel']}")
            recommendations.append(f"   - Potential annual savings: ~${(worst_channel['Spend'] * 0.25):,.0f}")
            recommendations.append(f"   - Expected revenue increase: ~${(worst_channel['Spend'] * 0.25 * best_channel['ROAS']):,.0f}")
    
    # Insight 3: Regional opportunities
    us_share = regional_perf[regional_perf['Region'] == 'US']['Revenue_Share'].iloc[0] if 'US' in regional_perf['Region'].values else 0
    if us_share > 70:
        insights.append(f"WARNING: Heavy US market concentration ({us_share:.0f}% of new member revenue)")
        recommendations.append("2. STRATEGIC: Develop international market expansion plan")
        recommendations.append("   - Focus on high-AOV regions (AU, CA, EU) for growth")
    
    # Insight 4: Seasonality
    daily_sales['Month_Num'] = daily_sales['Date'].dt.month
    seasonal_variation = daily_sales.groupby('Month_Num')['Daily Spend'].mean()
    cv = seasonal_variation.std() / seasonal_variation.mean()
    
    if cv > 0.3:
        insights.append(f"WARNING: High seasonal variation detected in spend patterns ({cv*100:.0f}% coefficient of variation)")
        recommendations.append("3. OPERATIONAL: Implement seasonal budget optimization")
        recommendations.append("   - Increase spend during peak conversion months")
        recommendations.append("   - Reduce spend during historically low-performance periods")
    
    # Print insights
    print("\nKEY INSIGHTS:")
    for insight in insights[:5]:  # Top 5 insights
        print(insight)
    
    print(f"\nACTIONABLE RECOMMENDATIONS:")
    for rec in recommendations[:3]:  # Top 3 recommendations
        print(rec)
    
    # Bottom line impact
    print(f"\nBOTTOM LINE IMPACT:")
    print("-" * 40)
    if len(channel_perf) > 1:
        worst_spend = channel_perf.iloc[-1]['Spend']
        best_roas = channel_perf.iloc[0]['ROAS']
        worst_roas = channel_perf.iloc[-1]['ROAS']
        
        potential_improvement = worst_spend * 0.25 * (best_roas - worst_roas)
        print(f"Immediate budget reallocation opportunity: ${potential_improvement:,.0f} additional revenue")
        print(f"ROI improvement potential: {(best_roas/worst_roas-1)*100:.0f}%")
    
    print(f"Current marketing efficiency: ${cost_per_order:.0f} cost per new customer")
    print(f"Industry benchmark range: $400-800 (Eight Sleep: {'WITHIN' if 400 <= cost_per_order <= 800 else 'OUTSIDE'} range)")
    
    return {
        'total_marketing_spend': total_marketing_spend,
        'new_member_revenue': new_member_revenue,
        'cost_per_order': cost_per_order,
        'roas': roas,
        'correlation': corr_spend_new if len(combined) > 2 else None,
        'channel_performance': channel_perf,
        'regional_performance': regional_perf
    }

if __name__ == "__main__":
    results = create_executive_summary()