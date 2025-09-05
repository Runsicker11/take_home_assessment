"""
Eight Sleep Advanced Attribution Analysis

This script performs sophisticated marketing attribution analysis to understand:
1. Cross-channel correlations and assist values
2. Time-lagged effects between awareness and conversion channels
3. Channel-specific data quality issues
4. True ROI of controllable channels (YouTube, FB)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr
import warnings
warnings.filterwarnings('ignore')

class AttributionAnalyzer:
    """Advanced attribution analysis for Eight Sleep marketing data"""
    
    def __init__(self, data_path='Raw Data/monthly_marketing_channel_level.csv'):
        self.data_path = data_path
        self.df = None
        self.monthly_data = None
        
    def load_and_clean_data(self):
        """Load and clean the marketing data with proper attribution focus"""
        print("Loading data for attribution analysis...")
        
        self.df = pd.read_csv(self.data_path)
        
        # Clean monetary values
        def clean_monetary_value(val):
            if pd.isna(val) or val == '':
                return 0
            if isinstance(val, str):
                return float(val.replace('$', '').replace(',', '').strip())
            return float(val)
        
        self.df['Spend'] = self.df['Spend'].apply(clean_monetary_value)
        self.df['Last Click Revenue'] = self.df['Last Click Revenue'].apply(clean_monetary_value)
        self.df['Month'] = pd.to_datetime(self.df['Month'], format='%m/%d/%Y %H:%M')
        
        # Convert numeric columns
        numeric_cols = ['Visitors', 'Last Click Add To Cart', 'Last Click Orders', 
                       'Last Click Email Captures', 'Email capture conversions 30 day window',
                       'Email capture conversions 60 day window']
        
        for col in numeric_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0).astype(int)
        
        # Flag cart/order anomalies
        self.df['cart_order_anomaly'] = self.df['Last Click Orders'] > self.df['Last Click Add To Cart']
        
        print(f"Loaded {len(self.df)} records across {len(self.df['Channel'].unique())} channels")
        return self
    
    def prepare_monthly_data(self):
        """Prepare data at monthly level for correlation analysis"""
        print("Preparing monthly aggregated data...")
        
        # Create monthly pivot table for each channel
        channels = ['YouTube Ads', 'FB Ads', 'Google Ads', 'Organic + Direct']
        
        monthly_list = []
        for month in self.df['Month'].unique():
            month_data = {'Month': month}
            month_df = self.df[self.df['Month'] == month]
            
            for channel in channels:
                channel_data = month_df[month_df['Channel'] == channel]
                if len(channel_data) > 0:
                    row = channel_data.iloc[0]
                    month_data[f'{channel}_Spend'] = row['Spend']
                    month_data[f'{channel}_Visitors'] = row['Visitors']
                    month_data[f'{channel}_Orders'] = row['Last Click Orders']
                    month_data[f'{channel}_Revenue'] = row['Last Click Revenue']
                    month_data[f'{channel}_EmailCaptures'] = row['Last Click Email Captures']
                else:
                    month_data[f'{channel}_Spend'] = 0
                    month_data[f'{channel}_Visitors'] = 0
                    month_data[f'{channel}_Orders'] = 0
                    month_data[f'{channel}_Revenue'] = 0
                    month_data[f'{channel}_EmailCaptures'] = 0
            
            monthly_list.append(month_data)
        
        self.monthly_data = pd.DataFrame(monthly_list).sort_values('Month').reset_index(drop=True)
        print(f"Created monthly dataset with {len(self.monthly_data)} months")
        return self
    
    def analyze_cross_channel_correlations(self):
        """Analyze correlations between paid channels and organic/google performance"""
        print("\\nAnalyzing cross-channel correlations and attribution...")
        
        results = {
            'same_month_correlations': {},
            'lagged_correlations': {},
            'statistical_significance': {}
        }
        
        # Define awareness channels (controllable) and conversion channels  
        awareness_channels = ['YouTube Ads', 'FB Ads']
        conversion_channels = ['Google Ads', 'Organic + Direct']
        
        print("\\n" + "="*60)
        print("CROSS-CHANNEL ATTRIBUTION ANALYSIS")
        print("="*60)
        
        # Same month correlations
        print("\\n1. SAME-MONTH CORRELATIONS:")
        for awareness in awareness_channels:
            for conversion in conversion_channels:
                for metric in ['Visitors', 'Orders', 'Revenue']:
                    awareness_data = self.monthly_data[f'{awareness}_Spend'].replace(0, np.nan).dropna()
                    conversion_data = self.monthly_data[f'{conversion}_{metric}']
                    
                    # Align the data (only months where awareness channel had spend)
                    valid_months = awareness_data.index
                    if len(valid_months) > 3:  # Need sufficient data
                        awareness_vals = awareness_data.loc[valid_months]
                        conversion_vals = conversion_data.loc[valid_months]
                        
                        if len(awareness_vals) > 3 and awareness_vals.std() > 0 and conversion_vals.std() > 0:
                            corr, p_value = pearsonr(awareness_vals, conversion_vals)
                            
                            key = f"{awareness}_spend_vs_{conversion}_{metric}"
                            results['same_month_correlations'][key] = corr
                            results['statistical_significance'][key] = p_value
                            
                            significance = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""
                            print(f"   {awareness} Spend → {conversion} {metric}: {corr:.3f} (p={p_value:.3f}) {significance}")
        
        # Time-lagged correlations (1-3 month lags)
        print("\\n2. TIME-LAGGED CORRELATIONS (Attribution Effects):")
        for lag in range(1, 4):  # 1, 2, 3 month lags
            print(f"\\n   {lag}-Month Lag Effects:")
            for awareness in awareness_channels:
                for conversion in conversion_channels:
                    for metric in ['Visitors', 'Orders', 'Revenue']:
                        awareness_data = self.monthly_data[f'{awareness}_Spend'].replace(0, np.nan)
                        conversion_data = self.monthly_data[f'{conversion}_{metric}'].shift(-lag)  # Shift conversion data back
                        
                        # Find valid overlap
                        valid_data = pd.concat([awareness_data, conversion_data], axis=1).dropna()
                        
                        if len(valid_data) > 3:
                            awareness_vals = valid_data.iloc[:, 0]
                            conversion_vals = valid_data.iloc[:, 1]
                            
                            if awareness_vals.std() > 0 and conversion_vals.std() > 0:
                                corr, p_value = pearsonr(awareness_vals, conversion_vals)
                                
                                key = f"{awareness}_spend_vs_{conversion}_{metric}_lag{lag}"
                                results['lagged_correlations'][key] = corr
                                results['statistical_significance'][key] = p_value
                                
                                significance = "***" if p_value < 0.001 else "**" if p_value < 0.01 else "*" if p_value < 0.05 else ""
                                print(f"      {awareness} Spend (t) → {conversion} {metric} (t+{lag}): {corr:.3f} (p={p_value:.3f}) {significance}")
        
        self.attribution_results = results
        return self
    
    def analyze_data_quality_by_channel(self):
        """Deep dive into data quality issues by specific channel"""
        print("\\n" + "="*60)
        print("DATA QUALITY ANALYSIS BY CHANNEL")
        print("="*60)
        
        # Cart/Order anomaly analysis by channel
        print("\\n1. CART/ORDER ANOMALIES BY CHANNEL:")
        anomaly_summary = self.df.groupby('Channel').agg({
            'cart_order_anomaly': ['count', 'sum'],
            'Last Click Orders': 'sum',
            'Last Click Add To Cart': 'sum'
        }).round(2)
        
        anomaly_summary.columns = ['Total_Records', 'Anomaly_Count', 'Total_Orders', 'Total_Carts']
        anomaly_summary['Anomaly_Rate'] = (anomaly_summary['Anomaly_Count'] / anomaly_summary['Total_Records'] * 100).round(1)
        anomaly_summary['Orders_vs_Carts_Ratio'] = (anomaly_summary['Total_Orders'] / anomaly_summary['Total_Carts'].replace(0, np.nan)).round(2)
        
        print(anomaly_summary[['Anomaly_Count', 'Anomaly_Rate', 'Orders_vs_Carts_Ratio']])
        
        # Channel-specific conversion patterns
        print("\\n2. CONVERSION PATTERNS BY CHANNEL:")
        conversion_analysis = self.df.groupby('Channel').agg({
            'Visitors': 'sum',
            'Last Click Add To Cart': 'sum', 
            'Last Click Orders': 'sum',
            'Last Click Revenue': 'sum'
        })
        
        conversion_analysis['Visitor_to_Cart_Rate'] = (conversion_analysis['Last Click Add To Cart'] / conversion_analysis['Visitors'] * 100).round(3)
        conversion_analysis['Cart_to_Order_Rate'] = (conversion_analysis['Last Click Orders'] / conversion_analysis['Last Click Add To Cart'].replace(0, np.nan) * 100).round(1)
        conversion_analysis['Overall_CR'] = (conversion_analysis['Last Click Orders'] / conversion_analysis['Visitors'] * 100).round(3)
        
        print(conversion_analysis[['Visitor_to_Cart_Rate', 'Cart_to_Order_Rate', 'Overall_CR']])
        
        # Organic + Direct deep dive
        print("\\n3. ORGANIC + DIRECT DEEP DIVE:")
        organic_data = self.df[self.df['Channel'] == 'Organic + Direct'].copy()
        organic_anomalies = organic_data[organic_data['cart_order_anomaly']]
        
        print(f"   Total Organic records: {len(organic_data)}")
        print(f"   Anomaly records: {len(organic_anomalies)} ({len(organic_anomalies)/len(organic_data)*100:.1f}%)")
        
        if len(organic_anomalies) > 0:
            print("\\n   Organic Anomaly Examples (Orders > Carts):")
            sample = organic_anomalies[['Month', 'Last Click Add To Cart', 'Last Click Orders']].head()
            for _, row in sample.iterrows():
                print(f"      {row['Month'].strftime('%Y-%m')}: {row['Last Click Orders']} orders > {row['Last Click Add To Cart']} carts")
        
        return self
    
    def calculate_youtube_email_vs_conversion_roi(self):
        """Analyze YouTube email capture vs direct conversion strategy ROI"""
        print("\\n" + "="*60) 
        print("YOUTUBE EMAIL CAPTURE vs DIRECT CONVERSION ANALYSIS")
        print("="*60)
        
        youtube_data = self.df[self.df['Channel'] == 'YouTube Ads'].copy()
        
        # Current performance metrics
        total_spend = youtube_data['Spend'].sum()
        total_visitors = youtube_data['Visitors'].sum()
        total_orders = youtube_data['Last Click Orders'].sum() 
        total_revenue = youtube_data['Last Click Revenue'].sum()
        total_emails = youtube_data['Last Click Email Captures'].sum()
        total_email_conv_30d = youtube_data['Email capture conversions 30 day window'].sum()
        total_email_conv_60d = youtube_data['Email capture conversions 60 day window'].sum()
        
        print(f"\\n1. CURRENT YOUTUBE PERFORMANCE:")
        print(f"   Total Spend: ${total_spend:,.0f}")
        print(f"   Total Visitors: {total_visitors:,.0f}")
        print(f"   Direct Orders: {total_orders:,.0f}")
        print(f"   Direct Revenue: ${total_revenue:,.0f}")
        print(f"   Email Captures: {total_emails:,.0f}")
        print(f"   Email → Orders (30d): {total_email_conv_30d:,.0f}")
        print(f"   Email → Orders (60d): {total_email_conv_60d:,.0f}")
        
        # Calculate rates
        email_capture_rate = total_emails / total_visitors
        direct_conversion_rate = total_orders / total_visitors
        email_30d_conversion = total_email_conv_30d / total_emails if total_emails > 0 else 0
        email_60d_conversion = total_email_conv_60d / total_emails if total_emails > 0 else 0
        
        print(f"\\n2. CONVERSION RATES:")
        print(f"   Email Capture Rate: {email_capture_rate*100:.2f}%")
        print(f"   Direct Conversion Rate: {direct_conversion_rate*100:.3f}%")
        print(f"   Email → Sale (30d): {email_30d_conversion*100:.2f}%")
        print(f"   Email → Sale (60d): {email_60d_conversion*100:.2f}%")
        
        # ROI Analysis
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 4250  # Use overall AOV as fallback
        
        # Current ROI breakdown
        direct_roas = total_revenue / total_spend if total_spend > 0 else 0
        email_revenue_30d = total_email_conv_30d * avg_order_value
        email_revenue_60d = total_email_conv_60d * avg_order_value
        
        print(f"\\n3. ROI ANALYSIS:")
        print(f"   Average Order Value: ${avg_order_value:,.0f}")
        print(f"   Direct ROAS: {direct_roas:.2f}x")
        print(f"   Email Revenue (30d): ${email_revenue_30d:,.0f}")
        print(f"   Email Revenue (60d): ${email_revenue_60d:,.0f}")
        
        # Strategy comparison
        print(f"\\n4. STRATEGY COMPARISON:")
        
        # Current strategy: Focus on direct conversions
        current_cpa = total_spend / total_orders if total_orders > 0 else 0
        current_total_revenue = total_revenue + email_revenue_60d  # Include email conversions
        current_total_orders = total_orders + total_email_conv_60d
        current_blended_roas = current_total_revenue / total_spend if total_spend > 0 else 0
        
        print(f"   Current Strategy (Direct Focus):")
        print(f"      CPA: ${current_cpa:,.0f}")
        print(f"      Blended ROAS (incl. email): {current_blended_roas:.2f}x")
        print(f"      Total Revenue: ${current_total_revenue:,.0f}")
        
        # Email-focused strategy simulation
        # Assume we could double email capture rate with same spend by changing creative/landing pages
        potential_emails = total_emails * 2  # Conservative 2x improvement
        potential_email_orders_60d = potential_emails * email_60d_conversion
        potential_email_revenue = potential_email_orders_60d * avg_order_value
        
        # Assume direct orders decrease by 50% due to creative change
        adjusted_direct_orders = total_orders * 0.5
        adjusted_direct_revenue = adjusted_direct_orders * avg_order_value
        
        email_strategy_revenue = adjusted_direct_revenue + potential_email_revenue
        email_strategy_roas = email_strategy_revenue / total_spend if total_spend > 0 else 0
        
        print(f"\\n   Email-Focused Strategy (Simulation):")
        print(f"      Potential Emails: {potential_emails:,.0f} (2x current)")
        print(f"      Email → Orders (60d): {potential_email_orders_60d:,.0f}")
        print(f"      Adjusted Direct Orders: {adjusted_direct_orders:,.0f} (50% of current)")
        print(f"      Total Projected Revenue: ${email_strategy_revenue:,.0f}")
        print(f"      Projected ROAS: {email_strategy_roas:.2f}x")
        
        revenue_difference = email_strategy_revenue - current_total_revenue
        print(f"\\n   Strategy Impact: {'+' if revenue_difference > 0 else ''}${revenue_difference:,.0f} ({revenue_difference/current_total_revenue*100:+.1f}%)")
        
        return self
    
    def develop_controllable_channel_strategy(self):
        """Develop optimization strategy focused on YouTube and FB as controllable channels"""
        print("\\n" + "="*60)
        print("CONTROLLABLE CHANNEL STRATEGY (YOUTUBE & FB)")
        print("="*60)
        
        # Analysis of controllable channels
        controllable = self.df[self.df['Channel'].isin(['YouTube Ads', 'FB Ads'])].copy()
        
        performance_summary = controllable.groupby('Channel').agg({
            'Spend': 'sum',
            'Visitors': 'sum',
            'Last Click Orders': 'sum',
            'Last Click Revenue': 'sum',
            'Last Click Email Captures': 'sum'
        })
        
        # Calculate efficiency metrics
        performance_summary['ROAS'] = performance_summary['Last Click Revenue'] / performance_summary['Spend']
        performance_summary['CPA'] = performance_summary['Spend'] / performance_summary['Last Click Orders']
        performance_summary['Cost_per_Visitor'] = performance_summary['Spend'] / performance_summary['Visitors']
        performance_summary['Email_Capture_Rate'] = performance_summary['Last Click Email Captures'] / performance_summary['Visitors'] * 100
        performance_summary['Email_Cost'] = performance_summary['Spend'] / performance_summary['Last Click Email Captures']
        
        print("\\n1. CONTROLLABLE CHANNEL PERFORMANCE:")
        print(performance_summary.round(2))
        
        # Attribution-aware analysis
        print("\\n2. ATTRIBUTION-AWARE INSIGHTS:")
        
        # YouTube analysis
        youtube_total_spend = performance_summary.loc['YouTube Ads', 'Spend']
        youtube_direct_revenue = performance_summary.loc['YouTube Ads', 'Last Click Revenue']
        youtube_visitors = performance_summary.loc['YouTube Ads', 'Visitors']
        
        # Estimate YouTube's assist value based on correlations
        strongest_correlation = 0
        if hasattr(self, 'attribution_results'):
            correlations = self.attribution_results['same_month_correlations']
            for key, corr in correlations.items():
                if 'YouTube Ads' in key and 'Google Ads' in key and abs(corr) > abs(strongest_correlation):
                    strongest_correlation = corr
        
        print(f"\\n   YouTube Ads Analysis:")
        print(f"      Direct ROAS: {youtube_direct_revenue/youtube_total_spend:.2f}x")
        print(f"      Traffic Volume: {youtube_visitors:,.0f} visitors (awareness)")
        print(f"      Strongest correlation with Google: {strongest_correlation:.3f}")
        print(f"      Strategic Role: Awareness + Email Capture")
        
        # FB Ads analysis  
        fb_total_spend = performance_summary.loc['FB Ads', 'Spend']
        fb_direct_revenue = performance_summary.loc['FB Ads', 'Last Click Revenue']
        fb_conversion_rate = performance_summary.loc['FB Ads', 'Last Click Orders'] / performance_summary.loc['FB Ads', 'Visitors']
        
        print(f"\\n   FB Ads Analysis:")
        print(f"      Direct ROAS: {fb_direct_revenue/fb_total_spend:.2f}x")
        print(f"      Conversion Rate: {fb_conversion_rate*100:.3f}%")
        print(f"      Strategic Role: Direct Response + Retargeting")
        
        # Strategic recommendations
        print("\\n3. STRATEGIC RECOMMENDATIONS:")
        print("\\n   A. YouTube Ads Optimization:")
        print("      • Shift primary KPI from direct ROAS to email capture + assist value")
        print("      • Test 2x higher email capture rates with lead magnets")
        print("      • Implement 60-day email nurture sequences")
        print("      • Measure blended ROAS including Google Ads lift")
        
        print("\\n   B. FB Ads Optimization:")
        print("      • Focus on direct conversion optimization")
        print("      • Expand retargeting audiences from YouTube traffic")
        print("      • Test lookalike audiences based on email subscribers")
        
        print("\\n   C. Budget Allocation Strategy:")
        total_controllable_spend = youtube_total_spend + fb_total_spend
        youtube_share = youtube_total_spend / total_controllable_spend * 100
        fb_share = fb_total_spend / total_controllable_spend * 100
        
        print(f"      Current: YouTube {youtube_share:.0f}% / FB {fb_share:.0f}%")
        print(f"      Recommended: YouTube 70% (awareness) / FB 30% (conversion)")
        print(f"      Rationale: YouTube's true value is in awareness + attribution lift")
        
        return self
    
    def generate_executive_insights(self):
        """Generate key insights for executive summary"""
        print("\\n" + "="*60)
        print("EXECUTIVE INSIGHTS - ATTRIBUTION ANALYSIS")
        print("="*60)
        
        insights = []
        
        # Attribution insights
        if hasattr(self, 'attribution_results'):
            strongest_correlations = []
            for key, corr in self.attribution_results['same_month_correlations'].items():
                if abs(corr) > 0.3 and 'YouTube' in key and ('Google' in key or 'Organic' in key):
                    strongest_correlations.append((key, corr))
            
            if strongest_correlations:
                insights.append("Attribution Discovery: YouTube Ads shows measurable correlation with Google/Organic performance - challenging simple ROAS comparison")
        
        # Data quality insights
        organic_anomalies = len(self.df[(self.df['Channel'] == 'Organic + Direct') & (self.df['cart_order_anomaly'])])
        total_organic = len(self.df[self.df['Channel'] == 'Organic + Direct'])
        
        if organic_anomalies > 0:
            insights.append(f"Data Quality: {organic_anomalies}/{total_organic} Organic+Direct records show orders>carts - likely subscription renewals/direct checkout")
        
        # YouTube strategy insight
        youtube_data = self.df[self.df['Channel'] == 'YouTube Ads']
        total_youtube_emails = youtube_data['Last Click Email Captures'].sum()
        total_youtube_visitors = youtube_data['Visitors'].sum()
        email_capture_rate = total_youtube_emails / total_youtube_visitors * 100
        
        insights.append(f"YouTube Opportunity: {email_capture_rate:.1f}% email capture rate suggests pivot to lead generation vs direct conversion")
        
        # Controllable channel insight
        controllable_spend = self.df[self.df['Channel'].isin(['YouTube Ads', 'FB Ads'])]['Spend'].sum()
        total_spend = self.df['Spend'].sum()
        controllable_share = controllable_spend / total_spend * 100
        
        insights.append(f"Strategic Focus: Only {controllable_share:.0f}% of spend is truly controllable (YouTube + FB) - these channels need attribution-aware optimization")
        
        print("\\nKey Insights:")
        for i, insight in enumerate(insights, 1):
            print(f"{i}. {insight}")
        
        return insights

def main():
    """Run the advanced attribution analysis"""
    print("Eight Sleep Advanced Attribution Analysis")
    print("=" * 50)
    
    analyzer = AttributionAnalyzer()
    
    try:
        (analyzer
         .load_and_clean_data()
         .prepare_monthly_data()
         .analyze_cross_channel_correlations()
         .analyze_data_quality_by_channel()
         .calculate_youtube_email_vs_conversion_roi()
         .develop_controllable_channel_strategy()
         .generate_executive_insights())
        
        print("\\n" + "="*60)
        print("ANALYSIS COMPLETE")
        print("="*60)
        print("Advanced attribution analysis reveals the complexity beyond simple channel ROAS.")
        print("Focus recommendations on YouTube (awareness) and FB (conversion) optimization.")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()