# Eight Sleep Marketing Data Analysis

## Overview
This comprehensive analysis of Eight Sleep's 18-month marketing data provides both technical insights and executive-level strategic recommendations for marketing optimization.

## Deliverables

### 1. Technical Analysis (`eight_sleep_technical_analysis.ipynb`)
A comprehensive Jupyter notebook featuring:
- **Data Preprocessing**: Cleaning, revenue classification (product vs subscription)
- **Exploratory Data Analysis**: Channel performance, funnel analysis, time series trends
- **Advanced Analytics**: Customer journey mapping, email cohort analysis, seasonality detection
- **Anomaly Detection**: Cart/order discrepancies, statistical outliers, data quality issues
- **Time Series Forecasting**: 6-month revenue projections with confidence intervals
- **Strategic Recommendations**: Data-driven insights for budget reallocation and optimization

### 2. Executive Report (`eight_sleep_executive_report.html`)
A polished, interactive HTML report designed for stakeholders:
- **Clean Design**: Minimal layout with professional typography and consistent spacing
- **Interactive Visualizations**: Highcharts-powered charts with export capabilities
- **Executive Summary**: Key metrics and high-impact findings in business language
- **Strategic Insights**: Non-technical explanations of data patterns and their implications
- **Print-Optimized**: CSS styling for clean PDF export

### 3. Report Generator (`eight_sleep_report_generator.py`)
A standalone Python script that automates the analysis:
- **Data Processing**: Automated cleaning and metric calculation
- **Analysis Pipeline**: Comprehensive analytics workflow
- **JSON Export**: Machine-readable results for further processing
- **Console Summary**: Quick executive overview

## Key Findings

### 📊 Performance Summary (18 Months)
- **Total Spend**: $10.2M
- **Total Revenue**: $46.3M  
- **Overall ROAS**: 4.52x
- **Total Orders**: 10,893

### 🎯 Critical Insights
1. **Google Ads Excellence**: Delivers 4.57x ROAS with 65% of paid revenue
2. **YouTube Opportunity**: 5.7M visitors but only 0.02% conversion rate - major optimization potential
3. **Data Quality Issue**: 31% of records show orders exceeding add-to-carts (likely tracking issue)
4. **Organic Channel Strength**: 0.16% conversion rate with $0 spend
5. **Email Nurture Value**: 60-day windows show 50% higher conversions than 30-day

### 💡 Immediate Actions
1. **Fix Tracking Infrastructure**: Resolve cart/order data discrepancy
2. **Budget Reallocation**: Shift 20% of YouTube budget to Google Ads (+$1.6M annual impact)
3. **YouTube Optimization**: Focus on email capture vs direct conversion
4. **Seasonality Leverage**: Increase spend 30% in peak months (Nov-Dec, May-Jun)

## Installation & Usage

### Prerequisites
```bash
pip install -r requirements.txt
```

### Running the Analysis
```bash
# Generate automated analysis
python eight_sleep_report_generator.py

# Or open the Jupyter notebook for detailed exploration
jupyter notebook eight_sleep_technical_analysis.ipynb

# View executive report
open eight_sleep_executive_report.html
```

## Data Structure
The analysis expects a CSV file with the following columns:
- Channel, Spend, Month, Visitors
- Last Click Add To Cart, Last Click Orders, Last Click Revenue
- Last Click Email Captures
- Email capture conversions (30-day and 60-day windows)

## Technical Approach

### Data Preprocessing
- Revenue classification: Orders classified as subscriptions ($200-400 AOV) vs products
- Anomaly flagging: Orders exceeding add-to-carts identified for investigation
- Metric calculation: ROAS, conversion rates, funnel metrics derived

### Advanced Analytics
- **Customer Journey**: Correlation analysis between YouTube awareness and Google conversions
- **Cohort Analysis**: Email capture performance across 30-day vs 60-day windows  
- **Seasonality**: Month-over-month patterns and seasonal indices
- **Forecasting**: Linear regression with seasonality for 6-month projections

### Anomaly Detection
- Month-over-month variance analysis (>50% change threshold)
- Statistical outliers using IQR method
- Data quality validation for impossible metrics

## Future Enhancements

### Priority Data Needs
1. **Multi-touch Attribution**: Understand YouTube's assist value in Google conversions
2. **Customer Lifetime Value**: By acquisition channel for better CPA optimization
3. **Product-Level Breakdown**: Separate mattress vs subscription performance
4. **Geographic Data**: State/city level performance for budget allocation
5. **Creative Performance**: Ad-level data within channels

### Recommended Integrations
- **Attribution Modeling**: Implement data-driven attribution
- **Predictive Analytics**: Customer LTV and churn prediction models  
- **Real-time Dashboards**: Automated monitoring of key metrics
- **A/B Testing Framework**: Systematic optimization testing

## Contact
Generated with Claude Code - For questions or enhancements, please review the technical notebook for detailed methodology and assumptions.