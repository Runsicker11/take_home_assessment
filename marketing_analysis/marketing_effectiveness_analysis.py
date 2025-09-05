import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import pearsonr, spearmanr
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")

class MarketingEffectivenessAnalyzer:
    def __init__(self):
        self.daily_sales = None
        self.regional_sales = None
        self.marketing_data = None
        self.monthly_aggregates = None
        self.new_members_monthly = None
        
    def load_and_clean_data(self):
        """Load and clean all datasets"""
        print("=== LOADING AND CLEANING DATA ===")
        
        # Load daily sales data
        print("Loading daily sales data...")
        self.daily_sales = pd.read_csv('Raw Data/daily_sales.csv')
        print(f"Daily sales shape: {self.daily_sales.shape}")
        
        # Clean daily sales data
        self.daily_sales['Date'] = pd.to_datetime(self.daily_sales['Date'])
        
        # Clean currency columns
        for col in ['Daily Spend', 'Bookings']:
            if self.daily_sales[col].dtype == 'object':
                self.daily_sales[col] = (self.daily_sales[col]
                                       .astype(str)
                                       .str.replace('$', '')
                                       .str.replace(',', '')
                                       .str.strip()
                                       .astype(float))
            else:
                self.daily_sales[col] = self.daily_sales[col].astype(float)
        
        # Clean numeric columns
        for col in ['Orders', 'Visitors']:
            if self.daily_sales[col].dtype == 'object':
                self.daily_sales[col] = (self.daily_sales[col]
                                       .astype(str)
                                       .str.replace(',', '')
                                       .str.strip()
                                       .astype(int))
            else:
                self.daily_sales[col] = self.daily_sales[col].astype(int)
        
        # Load regional sales data
        print("Loading regional sales data...")
        self.regional_sales = pd.read_csv('Raw Data/regional_sales.csv')
        print(f"Regional sales shape: {self.regional_sales.shape}")
        
        # Clean regional sales data
        self.regional_sales['Date'] = pd.to_datetime(self.regional_sales['Date'])
        if self.regional_sales['Bookings'].dtype == 'object':
            self.regional_sales['Bookings'] = (self.regional_sales['Bookings']
                                             .astype(str)
                                             .str.replace('$', '')
                                             .str.replace(',', '')
                                             .str.strip()
                                             .astype(float))
        else:
            self.regional_sales['Bookings'] = self.regional_sales['Bookings'].astype(float)
        
        # Load marketing data
        print("Loading marketing data...")
        self.marketing_data = pd.read_csv('Raw Data/monthly_marketing_channel_level.csv')
        print(f"Marketing data shape: {self.marketing_data.shape}")
        
        # Clean marketing data
        self.marketing_data['Month'] = pd.to_datetime(self.marketing_data['Month'])
        self.marketing_data['Spend'] = self.marketing_data['Spend'].fillna('$0')
        if self.marketing_data['Spend'].dtype == 'object':
            self.marketing_data['Spend'] = (self.marketing_data['Spend']
                                          .astype(str)
                                          .str.replace('$', '')
                                          .str.replace(',', '')
                                          .str.strip()
                                          .astype(float))
        else:
            self.marketing_data['Spend'] = self.marketing_data['Spend'].astype(float)
        
        print("Data cleaning completed successfully!")
        
    def calculate_monthly_aggregates(self):
        """Calculate monthly aggregates from daily data"""
        print("\n=== CALCULATING MONTHLY AGGREGATES ===")
        
        # Create month-year column for daily data
        self.daily_sales['Month'] = self.daily_sales['Date'].dt.to_period('M')
        
        # Aggregate daily data by month
        self.monthly_aggregates = self.daily_sales.groupby('Month').agg({
            'Daily Spend': 'sum',
            'Orders': 'sum',
            'Bookings': 'sum',
            'Visitors': 'sum'
        }).reset_index()
        
        # Convert Period to datetime for easier merging
        self.monthly_aggregates['Month'] = self.monthly_aggregates['Month'].dt.to_timestamp()
        
        print(f"Monthly aggregates shape: {self.monthly_aggregates.shape}")
        print("Sample monthly aggregates:")
        print(self.monthly_aggregates.head())
        
    def extract_new_members_revenue(self):
        """Extract new members revenue by month from regional data"""
        print("\n=== EXTRACTING NEW MEMBERS REVENUE ===")
        
        # Filter for new members only
        new_members_data = self.regional_sales[
            self.regional_sales['Customer Type'] == '1. New Members'
        ].copy()
        
        # Create month column
        new_members_data['Month'] = new_members_data['Date'].dt.to_period('M')
        
        # Aggregate new members data by month and region
        new_members_monthly = new_members_data.groupby(['Month', 'Region']).agg({
            'Bookings': 'sum',
            'Orders': 'sum',
            'Units': 'sum'
        }).reset_index()
        
        # Total new members by month (across all regions)
        self.new_members_monthly = new_members_data.groupby('Month').agg({
            'Bookings': 'sum',
            'Orders': 'sum',
            'Units': 'sum'
        }).reset_index()
        
        # Convert Period to datetime
        self.new_members_monthly['Month'] = self.new_members_monthly['Month'].dt.to_timestamp()
        new_members_monthly['Month'] = new_members_monthly['Month'].dt.to_timestamp()
        
        print(f"New members monthly shape: {self.new_members_monthly.shape}")
        print("Sample new members data:")
        print(self.new_members_monthly.head())
        
        # Store regional breakdown for later analysis
        self.new_members_regional = new_members_monthly
        
    def analyze_marketing_spend_trends(self):
        """Analyze marketing spend by channel and month"""
        print("\n=== MARKETING SPEND ANALYSIS ===")
        
        # Aggregate marketing spend by month (across all channels)
        marketing_monthly = self.marketing_data.groupby('Month').agg({
            'Spend': 'sum',
            'Visitors': 'sum',
            'Last Click Orders': 'sum',
            'Last Click Revenue': 'sum'
        }).reset_index()
        
        print("Marketing spend by month:")
        print(marketing_monthly.sort_values('Month'))
        
        # Analyze by channel
        channel_analysis = self.marketing_data.groupby('Channel').agg({
            'Spend': 'sum',
            'Visitors': 'sum',
            'Last Click Orders': 'sum',
            'Last Click Revenue': 'sum'
        }).reset_index()
        
        # Calculate efficiency metrics
        channel_analysis['Cost_per_Order'] = channel_analysis['Spend'] / channel_analysis['Last Click Orders']
        channel_analysis['ROAS'] = channel_analysis['Last Click Revenue'] / channel_analysis['Spend']
        
        print("\nChannel effectiveness analysis:")
        print(channel_analysis.sort_values('Spend', ascending=False))
        
        return marketing_monthly, channel_analysis
        
    def compare_trends(self):
        """Compare trends between marketing spend and new customer acquisition"""
        print("\n=== TREND COMPARISON ANALYSIS ===")
        
        # Get marketing monthly data
        marketing_monthly, channel_analysis = self.analyze_marketing_spend_trends()
        
        # Merge all monthly data
        combined_monthly = pd.merge(
            self.monthly_aggregates,
            self.new_members_monthly,
            on='Month',
            suffixes=('_daily', '_new_members'),
            how='outer'
        )
        
        combined_monthly = pd.merge(
            combined_monthly,
            marketing_monthly,
            on='Month',
            how='outer'
        )
        
        combined_monthly = combined_monthly.sort_values('Month')
        print("Combined monthly data:")
        print(combined_monthly)
        
        # Calculate correlations
        print("\n=== CORRELATION ANALYSIS ===")
        
        # Remove rows with NaN values for correlation analysis
        correlation_data = combined_monthly.dropna()
        
        if len(correlation_data) < 3:
            print("WARNING: Insufficient data points for meaningful correlation analysis")
            return combined_monthly, channel_analysis
        
        # Marketing spend vs new member bookings
        if 'Spend' in correlation_data.columns and 'Bookings_new_members' in correlation_data.columns:
            corr_spend_bookings, p_val_spend = pearsonr(
                correlation_data['Spend'], 
                correlation_data['Bookings_new_members']
            )
            print(f"Marketing Spend vs New Member Bookings: r={corr_spend_bookings:.3f}, p={p_val_spend:.3f}")
        
        # Daily spend vs new member orders
        if 'Daily Spend' in correlation_data.columns and 'Orders_new_members' in correlation_data.columns:
            corr_daily_orders, p_val_daily = pearsonr(
                correlation_data['Daily Spend'], 
                correlation_data['Orders_new_members']
            )
            print(f"Daily Spend vs New Member Orders: r={corr_daily_orders:.3f}, p={p_val_daily:.3f}")
        
        # Visitors vs new members
        if 'Visitors_y' in correlation_data.columns and 'Orders_new_members' in correlation_data.columns:
            corr_visitors_orders, p_val_visitors = pearsonr(
                correlation_data['Visitors_y'], 
                correlation_data['Orders_new_members']
            )
            print(f"Marketing Visitors vs New Member Orders: r={corr_visitors_orders:.3f}, p={p_val_visitors:.3f}")
        
        return combined_monthly, channel_analysis
        
    def analyze_daily_patterns(self):
        """Analyze daily patterns between spend and new customer acquisition"""
        print("\n=== DAILY PATTERN ANALYSIS ===")
        
        # Get daily new members data
        daily_new_members = self.regional_sales[
            self.regional_sales['Customer Type'] == '1. New Members'
        ].groupby('Date').agg({
            'Bookings': 'sum',
            'Orders': 'sum'
        }).reset_index()
        
        # Merge with daily sales
        daily_combined = pd.merge(
            self.daily_sales,
            daily_new_members,
            on='Date',
            suffixes=('_total', '_new_members'),
            how='left'
        )
        
        # Fill NaN values with 0 for new members (days with no new member sales)
        daily_combined['Bookings_new_members'].fillna(0, inplace=True)
        daily_combined['Orders_new_members'].fillna(0, inplace=True)
        
        print(f"Daily combined data shape: {daily_combined.shape}")
        
        # Calculate correlations
        corr_daily_spend_bookings, p_val_daily_spend = pearsonr(
            daily_combined['Daily Spend'], 
            daily_combined['Bookings_new_members']
        )
        
        corr_daily_spend_orders, p_val_daily_orders = pearsonr(
            daily_combined['Daily Spend'], 
            daily_combined['Orders_new_members']
        )
        
        print(f"Daily Spend vs New Member Bookings: r={corr_daily_spend_bookings:.3f}, p={p_val_daily_spend:.3f}")
        print(f"Daily Spend vs New Member Orders: r={corr_daily_spend_orders:.3f}, p={p_val_daily_orders:.3f}")
        
        # Look for days with high spend but low new customer acquisition
        daily_combined['Spend_per_New_Order'] = daily_combined['Daily Spend'] / (daily_combined['Orders_new_members'] + 1)  # +1 to avoid division by zero
        
        # Identify potential waste (high spend, low new acquisition)
        high_spend_threshold = daily_combined['Daily Spend'].quantile(0.8)
        low_acquisition_threshold = daily_combined['Orders_new_members'].quantile(0.2)
        
        potential_waste = daily_combined[
            (daily_combined['Daily Spend'] >= high_spend_threshold) &
            (daily_combined['Orders_new_members'] <= low_acquisition_threshold)
        ]
        
        print(f"\nPotential waste days (high spend, low new customer acquisition): {len(potential_waste)} days")
        if len(potential_waste) > 0:
            print("Sample waste days:")
            print(potential_waste[['Date', 'Daily Spend', 'Orders_new_members', 'Spend_per_New_Order']].head())
        
        return daily_combined, potential_waste
        
    def analyze_regional_patterns(self):
        """Analyze regional patterns that might suggest marketing effectiveness"""
        print("\n=== REGIONAL PATTERN ANALYSIS ===")
        
        # Aggregate new members by region
        regional_summary = self.regional_sales[
            self.regional_sales['Customer Type'] == '1. New Members'
        ].groupby('Region').agg({
            'Bookings': 'sum',
            'Orders': 'sum',
            'Units': 'sum'
        }).reset_index()
        
        regional_summary['Avg_Order_Value'] = regional_summary['Bookings'] / regional_summary['Orders']
        regional_summary = regional_summary.sort_values('Bookings', ascending=False)
        
        print("Regional new member performance:")
        print(regional_summary)
        
        # Time series by region to look for patterns
        regional_time_series = self.regional_sales[
            self.regional_sales['Customer Type'] == '1. New Members'
        ].copy()
        regional_time_series['Month'] = regional_time_series['Date'].dt.to_period('M')
        
        regional_monthly = regional_time_series.groupby(['Month', 'Region']).agg({
            'Bookings': 'sum',
            'Orders': 'sum'
        }).reset_index()
        
        print("\nRegional monthly trends (sample):")
        print(regional_monthly.head(10))
        
        return regional_summary, regional_monthly
        
    def critical_analysis(self, combined_monthly, daily_combined, channel_analysis):
        """Apply critical analysis to identify meaningful patterns and confounding factors"""
        print("\n" + "="*50)
        print("CRITICAL ANALYSIS - EXECUTIVE SUMMARY")
        print("="*50)
        
        # Sample size assessment
        monthly_data_points = len(combined_monthly.dropna())
        daily_data_points = len(daily_combined)
        
        print(f"Data availability:")
        print(f"- Monthly data points: {monthly_data_points}")
        print(f"- Daily data points: {daily_data_points}")
        print(f"- Time period: {self.daily_sales['Date'].min()} to {self.daily_sales['Date'].max()}")
        
        # Statistical significance assessment
        print(f"\nStatistical Assessment:")
        if monthly_data_points < 12:
            print(f"WARNING: Only {monthly_data_points} months of data available. Results may not be statistically robust.")
        
        # Seasonality check
        self.daily_sales['Month_Num'] = self.daily_sales['Date'].dt.month
        monthly_avg_spend = self.daily_sales.groupby('Month_Num')['Daily Spend'].mean()
        
        seasonal_variation = (monthly_avg_spend.max() - monthly_avg_spend.min()) / monthly_avg_spend.mean()
        print(f"Seasonal variation in daily spend: {seasonal_variation:.1%}")
        
        if seasonal_variation > 0.3:
            print("WARNING: High seasonal variation detected. This may confound marketing effectiveness analysis.")
        
        # Marketing efficiency assessment
        print(f"\nMarketing Channel Efficiency:")
        print(f"- Total marketing spend: ${channel_analysis['Spend'].sum():,.0f}")
        print(f"- Total orders from marketing: {channel_analysis['Last Click Orders'].sum():,.0f}")
        print(f"- Average cost per order: ${channel_analysis['Spend'].sum() / channel_analysis['Last Click Orders'].sum():.0f}")
        
        # Identify best and worst performing channels
        valid_channels = channel_analysis[channel_analysis['Last Click Orders'] > 0].copy()
        if len(valid_channels) > 0:
            best_roas_channel = valid_channels.loc[valid_channels['ROAS'].idxmax()]
            worst_roas_channel = valid_channels.loc[valid_channels['ROAS'].idxmin()]
            
            print(f"- Best ROAS channel: {best_roas_channel['Channel']} (ROAS: {best_roas_channel['ROAS']:.1f}x)")
            print(f"- Worst ROAS channel: {worst_roas_channel['Channel']} (ROAS: {worst_roas_channel['ROAS']:.1f}x)")
        
        # Key findings
        print(f"\nKEY FINDINGS:")
        
        # 1. Overall correlation assessment
        if monthly_data_points >= 3:
            correlation_data = combined_monthly.dropna()
            if len(correlation_data) >= 3 and 'Spend' in correlation_data.columns and 'Bookings_new_members' in correlation_data.columns:
                corr_spend_bookings, p_val_spend = pearsonr(
                    correlation_data['Spend'], 
                    correlation_data['Bookings_new_members']
                )
                
                if abs(corr_spend_bookings) > 0.7 and p_val_spend < 0.05:
                    print(f"[STRONG] correlation between marketing spend and new customer acquisition (r={corr_spend_bookings:.3f}, p={p_val_spend:.3f})")
                elif abs(corr_spend_bookings) > 0.3 and p_val_spend < 0.10:
                    print(f"[MODERATE] correlation between marketing spend and new customer acquisition (r={corr_spend_bookings:.3f}, p={p_val_spend:.3f})")
                else:
                    print(f"[WEAK/NONE] correlation between marketing spend and new customer acquisition (r={corr_spend_bookings:.3f}, p={p_val_spend:.3f})")
        
        # 2. Daily patterns
        if 'Bookings_new_members' in daily_combined.columns:
            daily_corr, daily_p = pearsonr(daily_combined['Daily Spend'], daily_combined['Bookings_new_members'])
            if abs(daily_corr) > 0.3 and daily_p < 0.05:
                print(f"[YES] Daily spend shows meaningful correlation with new customer acquisition (r={daily_corr:.3f})")
            else:
                print(f"[NO] Daily spend shows weak correlation with new customer acquisition (r={daily_corr:.3f})")
        
        # 3. Channel performance assessment
        if len(valid_channels) > 1:
            roas_range = valid_channels['ROAS'].max() - valid_channels['ROAS'].min()
            if roas_range > 2:
                print(f"[SIGNIFICANT] channel performance differences detected (ROAS range: {roas_range:.1f}x)")
                print("  -> Opportunity to reallocate budget from underperforming to high-performing channels")
            else:
                print(f"[LIMITED] channel performance differences (ROAS range: {roas_range:.1f}x)")
        
        # 4. Waste identification
        waste_percentage = len(daily_combined[daily_combined['Spend_per_New_Order'] > daily_combined['Spend_per_New_Order'].quantile(0.9)]) / len(daily_combined) * 100
        print(f"WASTE: {waste_percentage:.1f}% of days show potentially inefficient spend patterns")
        
        print(f"\n" + "="*50)
        print("RECOMMENDATIONS:")
        print("="*50)
        
        # Generate specific recommendations based on findings
        recommendations = []
        
        if monthly_data_points < 6:
            recommendations.append("EXTEND ANALYSIS PERIOD: Current data period is too short for robust conclusions. Collect 12+ months of data for reliable insights.")
        
        if len(valid_channels) > 1:
            best_channel = valid_channels.loc[valid_channels['ROAS'].idxmax()]
            worst_channel = valid_channels.loc[valid_channels['ROAS'].idxmin()]
            
            if best_channel['ROAS'] > worst_channel['ROAS'] * 2:
                recommendations.append(f"BUDGET REALLOCATION: Shift budget from {worst_channel['Channel']} (ROAS: {worst_channel['ROAS']:.1f}x) to {best_channel['Channel']} (ROAS: {best_channel['ROAS']:.1f}x)")
        
        if waste_percentage > 20:
            recommendations.append(f"OPTIMIZE SPEND TIMING: {waste_percentage:.1f}% of days show inefficient patterns. Analyze day-of-week and seasonal effects.")
        
        recommendations.append("IMPLEMENT ATTRIBUTION MODELING: Current analysis uses last-click attribution. Consider view-through and multi-touch attribution for complete picture.")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
        
        return {
            'monthly_data_points': monthly_data_points,
            'seasonal_variation': seasonal_variation,
            'waste_percentage': waste_percentage,
            'recommendations': recommendations
        }
        
    def run_full_analysis(self):
        """Run the complete analysis pipeline"""
        print("EIGHT SLEEP - MARKETING EFFECTIVENESS ANALYSIS")
        print("=" * 60)
        
        # Load and clean data
        self.load_and_clean_data()
        
        # Calculate aggregates
        self.calculate_monthly_aggregates()
        
        # Extract new members data
        self.extract_new_members_revenue()
        
        # Compare trends
        combined_monthly, channel_analysis = self.compare_trends()
        
        # Analyze daily patterns
        daily_combined, potential_waste = self.analyze_daily_patterns()
        
        # Analyze regional patterns
        regional_summary, regional_monthly = self.analyze_regional_patterns()
        
        # Critical analysis
        analysis_results = self.critical_analysis(combined_monthly, daily_combined, channel_analysis)
        
        return {
            'combined_monthly': combined_monthly,
            'daily_combined': daily_combined,
            'channel_analysis': channel_analysis,
            'regional_summary': regional_summary,
            'potential_waste': potential_waste,
            'analysis_results': analysis_results
        }

# Run the analysis
if __name__ == "__main__":
    analyzer = MarketingEffectivenessAnalyzer()
    results = analyzer.run_full_analysis()
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print("Results stored in 'results' dictionary with the following keys:")
    for key in results.keys():
        print(f"- {key}")