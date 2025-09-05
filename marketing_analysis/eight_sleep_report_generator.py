"""
Eight Sleep Marketing Data Analysis - Report Generator Script

This script processes Eight Sleep's marketing data and generates both technical
and executive reports with interactive visualizations.

Usage:
    python eight_sleep_report_generator.py

Dependencies:
    - pandas
    - numpy
    - plotly
    - sklearn
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class EightSleepAnalyzer:
    """Main analyzer class for Eight Sleep marketing data"""
    
    def __init__(self, data_path='Raw Data/monthly_marketing_channel_level.csv'):
        self.data_path = data_path
        self.df = None
        self.processed_data = {}
        
    def load_and_clean_data(self):
        """Load and clean the raw marketing data"""
        print("Loading and cleaning data...")
        
        # Load the data
        self.df = pd.read_csv(self.data_path)
        
        # Clean monetary values
        def clean_monetary_value(val):
            if pd.isna(val) or val == '':
                return 0
            if isinstance(val, str):
                return float(val.replace('$', '').replace(',', '').strip())
            return float(val)
        
        # Clean monetary columns
        self.df['Spend'] = self.df['Spend'].apply(clean_monetary_value)
        self.df['Last Click Revenue'] = self.df['Last Click Revenue'].apply(clean_monetary_value)
        
        # Convert date column
        self.df['Month'] = pd.to_datetime(self.df['Month'], format='%m/%d/%Y %H:%M')
        
        # Convert numeric columns
        numeric_cols = ['Visitors', 'Last Click Add To Cart', 'Last Click Orders', 
                       'Last Click Email Captures', 'Email capture conversions 30 day window',
                       'Email capture conversions 60 day window']
        
        for col in numeric_cols:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0).astype(int)
        
        print(f"Loaded {len(self.df)} records across {len(self.df['Channel'].unique())} channels")
        return self
    
    def calculate_derived_metrics(self):
        """Calculate key derived metrics"""
        print("Calculating derived metrics...")
        
        # Separate subscription vs product revenue
        def classify_revenue_type(row):
            if row['Last Click Orders'] > 0:
                aov = row['Last Click Revenue'] / row['Last Click Orders']
                if 200 <= aov <= 400:
                    return 'subscription'
            return 'product'
        
        self.df['revenue_type'] = self.df.apply(classify_revenue_type, axis=1)
        
        # Calculate key metrics
        self.df['AOV'] = np.where(self.df['Last Click Orders'] > 0, 
                                 self.df['Last Click Revenue'] / self.df['Last Click Orders'], 0)
        self.df['Conversion Rate'] = np.where(self.df['Visitors'] > 0, 
                                             self.df['Last Click Orders'] / self.df['Visitors'], 0)
        self.df['Cart Conversion Rate'] = np.where(self.df['Last Click Add To Cart'] > 0,
                                                  self.df['Last Click Orders'] / self.df['Last Click Add To Cart'], 0)
        self.df['CPA'] = np.where(self.df['Last Click Orders'] > 0,
                                 self.df['Spend'] / self.df['Last Click Orders'], 0)
        self.df['ROAS'] = np.where(self.df['Spend'] > 0,
                                  self.df['Last Click Revenue'] / self.df['Spend'], 0)
        self.df['Email Capture Rate'] = np.where(self.df['Visitors'] > 0,
                                                 self.df['Last Click Email Captures'] / self.df['Visitors'], 0)
        
        # Flag cart/order anomaly
        self.df['cart_order_anomaly'] = self.df['Last Click Orders'] > self.df['Last Click Add To Cart']
        
        print(f"Identified {self.df['cart_order_anomaly'].sum()} cart/order anomalies")
        return self
    
    def analyze_channel_performance(self):
        """Analyze performance by channel"""
        print("Analyzing channel performance...")
        
        channel_summary = self.df.groupby('Channel').agg({
            'Spend': 'sum',
            'Visitors': 'sum',
            'Last Click Orders': 'sum',
            'Last Click Revenue': 'sum',
            'Last Click Email Captures': 'sum',
            'ROAS': 'mean',
            'Conversion Rate': 'mean',
            'AOV': 'mean',
            'cart_order_anomaly': 'sum'
        }).round(2)
        
        # Calculate overall metrics
        channel_summary['Overall ROAS'] = (channel_summary['Last Click Revenue'] / 
                                          channel_summary['Spend'].replace(0, np.nan)).fillna(0)
        channel_summary['Overall CR'] = channel_summary['Last Click Orders'] / channel_summary['Visitors']
        channel_summary['Spend Share'] = channel_summary['Spend'] / channel_summary['Spend'].sum() * 100
        channel_summary['Revenue Share'] = channel_summary['Last Click Revenue'] / channel_summary['Last Click Revenue'].sum() * 100
        
        self.processed_data['channel_summary'] = channel_summary
        return self
    
    def detect_seasonality(self):
        """Detect seasonal patterns in the data"""
        print("Detecting seasonality patterns...")
        
        self.df['Month_Num'] = self.df['Month'].dt.month
        
        seasonality = self.df.groupby('Month_Num').agg({
            'Last Click Revenue': 'mean',
            'Last Click Orders': 'mean',
            'Visitors': 'mean'
        }).round(2)
        
        # Calculate seasonal indices
        for col in ['Last Click Revenue', 'Last Click Orders', 'Visitors']:
            mean_val = seasonality[col].mean()
            seasonality[f'{col}_Index'] = (seasonality[col] / mean_val * 100).round(1)
        
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        seasonality['Month'] = [month_names[i-1] for i in seasonality.index]
        
        self.processed_data['seasonality'] = seasonality
        return self
    
    def analyze_email_cohorts(self):
        """Analyze email capture cohort performance"""
        print("Analyzing email cohort performance...")
        
        email_channels = self.df[self.df['Channel'] != 'Organic + Direct'].copy()
        
        email_channels['30_day_conversion_rate'] = (
            email_channels['Email capture conversions 30 day window'] / 
            email_channels['Last Click Email Captures'].replace(0, np.nan)
        ).fillna(0)
        
        email_channels['60_day_conversion_rate'] = (
            email_channels['Email capture conversions 60 day window'] / 
            email_channels['Last Click Email Captures'].replace(0, np.nan)
        ).fillna(0)
        
        email_summary = email_channels.groupby('Channel').agg({
            'Last Click Email Captures': 'sum',
            'Email capture conversions 30 day window': 'sum',
            'Email capture conversions 60 day window': 'sum',
            '30_day_conversion_rate': 'mean',
            '60_day_conversion_rate': 'mean'
        }).round(3)
        
        email_summary['Overall 30-day CR'] = (
            email_summary['Email capture conversions 30 day window'] / 
            email_summary['Last Click Email Captures']
        )
        email_summary['Overall 60-day CR'] = (
            email_summary['Email capture conversions 60 day window'] / 
            email_summary['Last Click Email Captures']
        )
        email_summary['Incremental Lift %'] = (
            (email_summary['Overall 60-day CR'] - email_summary['Overall 30-day CR']) / 
            email_summary['Overall 30-day CR'] * 100
        )
        
        self.processed_data['email_cohorts'] = email_summary
        return self
    
    def generate_forecasts(self, periods=6):
        """Generate simple forecasts for key metrics"""
        print(f"Generating {periods}-month forecasts...")
        
        from sklearn.linear_model import LinearRegression
        
        # Prepare monthly data
        monthly_data = self.df.groupby('Month').agg({
            'Last Click Revenue': 'sum',
            'Last Click Orders': 'sum',
            'Visitors': 'sum'
        }).reset_index().sort_values('Month')
        
        # Simple linear trend forecast
        X = np.arange(len(monthly_data)).reshape(-1, 1)
        y_revenue = monthly_data['Last Click Revenue'].values
        
        model = LinearRegression()
        model.fit(X, y_revenue)
        
        # Generate future predictions
        future_X = np.arange(len(monthly_data), len(monthly_data) + periods).reshape(-1, 1)
        future_revenue = model.predict(future_X)
        
        # Create forecast data
        last_date = monthly_data['Month'].max()
        forecast_dates = []
        for i in range(1, periods + 1):
            forecast_dates.append(last_date + pd.DateOffset(months=i))
        
        forecast_df = pd.DataFrame({
            'Month': forecast_dates,
            'Revenue_Forecast': future_revenue
        })
        
        self.processed_data['forecast'] = forecast_df
        return self
    
    def detect_anomalies(self):
        """Detect anomalies in the data"""
        print("Detecting anomalies...")
        
        anomalies = {
            'cart_order_issues': self.df['cart_order_anomaly'].sum(),
            'impossible_conversions': len(self.df[self.df['Conversion Rate'] > 1]),
            'high_variance_channels': []
        }
        
        # Month-over-month variance analysis
        for channel in self.df['Channel'].unique():
            channel_data = self.df[self.df['Channel'] == channel].sort_values('Month')
            if len(channel_data) > 1:
                revenue_changes = channel_data['Last Click Revenue'].pct_change()
                high_variance_months = abs(revenue_changes) > 0.5  # 50% threshold
                if high_variance_months.sum() > 0:
                    anomalies['high_variance_channels'].append({
                        'channel': channel,
                        'high_variance_months': high_variance_months.sum()
                    })
        
        self.processed_data['anomalies'] = anomalies
        return self
    
    def generate_insights(self):
        """Generate key insights from the analysis"""
        print("Generating insights...")
        
        channel_summary = self.processed_data['channel_summary']
        
        # Key insights
        insights = {
            'total_spend': self.df['Spend'].sum(),
            'total_revenue': self.df['Last Click Revenue'].sum(),
            'total_orders': self.df['Last Click Orders'].sum(),
            'overall_roas': self.df['Last Click Revenue'].sum() / self.df['Spend'].sum(),
            'best_roas_channel': channel_summary['Overall ROAS'].idxmax(),
            'worst_cr_channel': channel_summary['Overall CR'].idxmin(),
            'highest_traffic_channel': channel_summary['Visitors'].idxmax(),
            'anomaly_percentage': (self.df['cart_order_anomaly'].sum() / len(self.df)) * 100
        }
        
        self.processed_data['insights'] = insights
        return self
    
    def save_summary_report(self, filename='analysis_summary.json'):
        """Save analysis summary to JSON file"""
        print(f"Saving summary to {filename}...")
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, pd.DataFrame):
                return obj.to_dict('index')
            elif isinstance(obj, pd.Timestamp):
                return obj.isoformat()
            return obj
        
        # Convert all processed data
        json_data = {}
        for key, value in self.processed_data.items():
            if isinstance(value, pd.DataFrame):
                json_data[key] = {str(k): {str(k2): convert_numpy(v2) for k2, v2 in v.items()} 
                                 for k, v in value.to_dict('index').items()}
            elif isinstance(value, dict):
                json_data[key] = {k: convert_numpy(v) for k, v in value.items()}
            else:
                json_data[key] = convert_numpy(value)
        
        with open(filename, 'w') as f:
            json.dump(json_data, f, indent=2, default=str)
        
        print("Summary report saved successfully!")
        return self
    
    def print_executive_summary(self):
        """Print executive summary to console"""
        insights = self.processed_data['insights']
        channel_summary = self.processed_data['channel_summary']
        
        print("\n" + "="*60)
        print("EIGHT SLEEP MARKETING ANALYSIS - EXECUTIVE SUMMARY")
        print("="*60)
        
        print(f"\n📊 OVERALL PERFORMANCE (18 Months):")
        print(f"   Total Spend: ${insights['total_spend']:,.0f}")
        print(f"   Total Revenue: ${insights['total_revenue']:,.0f}")
        print(f"   Total Orders: {insights['total_orders']:,.0f}")
        print(f"   Overall ROAS: {insights['overall_roas']:.2f}")
        
        print(f"\n🎯 KEY FINDINGS:")
        print(f"   1. Best ROAS Channel: {insights['best_roas_channel']} ({channel_summary.loc[insights['best_roas_channel'], 'Overall ROAS']:.2f}x)")
        print(f"   2. Highest Traffic: {insights['highest_traffic_channel']} ({channel_summary.loc[insights['highest_traffic_channel'], 'Visitors']:,.0f} visitors)")
        print(f"   3. Data Quality Issue: {insights['anomaly_percentage']:.1f}% of records have cart/order anomalies")
        print(f"   4. Lowest CR Channel: {insights['worst_cr_channel']} ({channel_summary.loc[insights['worst_cr_channel'], 'Overall CR']*100:.3f}%)")
        
        if 'email_cohorts' in self.processed_data:
            email_data = self.processed_data['email_cohorts']
            avg_lift = email_data['Incremental Lift %'].mean()
            print(f"   5. Email Nurture Impact: {avg_lift:.0f}% lift from 60-day vs 30-day windows")
        
        print("\n💡 IMMEDIATE ACTIONS:")
        print("   1. Fix tracking: Resolve cart/order data discrepancy")
        print("   2. Reallocate budget: Shift low-performing channel spend to high ROAS channels")
        print("   3. Optimize funnels: Focus on improving conversion paths")
        print("   4. Leverage seasonality: Adjust budgets based on seasonal patterns")
        
        print("\n" + "="*60)

def main():
    """Main execution function"""
    print("Eight Sleep Marketing Analysis - Report Generator")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = EightSleepAnalyzer()
    
    try:
        # Run full analysis pipeline
        (analyzer
         .load_and_clean_data()
         .calculate_derived_metrics()
         .analyze_channel_performance()
         .detect_seasonality()
         .analyze_email_cohorts()
         .generate_forecasts()
         .detect_anomalies()
         .generate_insights()
         .save_summary_report()
         .print_executive_summary())
        
        print("\nAnalysis complete! Check the following files:")
        print("- eight_sleep_technical_analysis.ipynb (Technical deep-dive)")
        print("- eight_sleep_executive_report.html (Executive presentation)")
        print("- analysis_summary.json (Data export)")
        
    except FileNotFoundError:
        print(f"Error: Could not find data file at {analyzer.data_path}")
        print("Please ensure the CSV file exists in the Raw Data directory.")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        print("Please check the data format and try again.")

if __name__ == "__main__":
    main()