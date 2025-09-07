# WBR Business Vitals Analysis

## 📊 Project Overview

This project provides comprehensive Weekly Business Review (WBR) analysis for business vitals including:
- Customer Acquisition Cost (CAC) tracking and trends
- Regional performance analysis
- Member lifecycle analysis (upgrades, renewals)
- CAC forecasting with diminishing returns modeling

## 📁 File Structure

```
wbr/
├── wbr_executive_report.html  # Main Interactive WBR Dashboard ⭐
├── wbr_data.json              # Processed business metrics data
├── wbr_report_puppeteer.html  # PDF-optimized HTML report
├── package.json               # Node.js dependencies
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. View Interactive Report
Open `wbr_executive_report.html` in any modern web browser to view the interactive dashboard with:
- Live KPI cards with week-over-week trends
- Interactive charts with hover tooltips
- Automated commentary and insights
- CAC forecast scenarios

### 2. Generate PDF Report

#### Method 1: Windows Batch Script (Easiest)
```bash
# Double-click or run from command line
generate_pdf.bat
```

#### Method 2: Node.js (Recommended for best quality)
```bash
# Install dependencies
npm install puppeteer

# Generate PDF
node generate_pdf.js
```

#### Method 3: Python
```bash
# Install dependencies
pip install playwright weasyprint

# For Playwright (recommended)
playwright install chromium

# Generate PDF
python generate_pdf.py
```

## 📋 Key Performance Indicators (KPIs)

The report tracks 8 core KPIs with WoW and MoM comparisons:

**Weekly Metrics:**
- New Customers (with WoW change)
- Booking Revenue (with WoW change) 
- Marketing Spend (with WoW change)
- CAC - Customer Acquisition Cost (with WoW change)

**Monthly Metrics:**
- New Customers (with MoM change)
- Booking Revenue (with MoM change)
- Marketing Spend (with MoM change)
- CAC - Customer Acquisition Cost (with MoM change)

## 📊 Report Sections

### Page 1: Executive Dashboard
- KPI cards with directional indicators
- Executive summary with key insights
- High-level performance overview

### Page 2: CAC Analysis
- Weekly CAC trend (8-week focus)
- Monthly CAC history (12-month context)
- Efficiency indicators and trend analysis

### Page 3: Regional Performance
- New customer orders by region
- Regional growth analysis (4-week comparisons)
- Market share breakdown

### Page 4: Lifecycle & Forecast
- Member upgrades vs renewals trends
- CAC forecast scenarios with diminishing returns
- Business implications and recommendations

## 🎯 Data Sources

- **daily_sales.csv**: 560 days of daily performance data (Jan 2024 - Jul 2025)
- **regional_sales.csv**: Regional breakdown by customer type (~9,850 records)

## 🔧 Technical Details

### CAC Calculation
```
CAC = Total Marketing Spend ÷ New Customer Orders
```
- Uses only "1. New Members" customer type for accurate attribution
- Calculated at daily, weekly, and monthly levels
- Includes WoW and MoM percentage change tracking

### Forecast Methodology
- Assumes 85% efficiency on incremental spend (diminishing returns)
- Models 5 scenarios: +10%, +20%, +30%, +50%, +100% spend increases
- Projects CAC impact under each scenario

### PDF Generation
- **Puppeteer** (Node.js): Best quality with full chart rendering
- **Playwright** (Python): Good quality alternative
- **WeasyPrint** (Python): Simple but limited chart support

## 📈 Chart Types Used

1. **Line Charts**: CAC trends, lifecycle analysis
2. **Column Charts**: Monthly comparisons, regional growth
3. **Bar Charts**: Regional performance breakdown
4. **Combination Charts**: CAC with WoW overlays

## 🎨 Design Features

- **Typography**: Helvetica Neue, 12pt base, professional hierarchy
- **Colors**: Muted 4-color palette (blue, green, orange, red)
- **Layout**: Grid-based with consistent spacing
- **Print Ready**: Optimized page breaks, fixed chart dimensions
- **Responsive**: Works on desktop and mobile browsers

## 🔍 Data Quality

- Comprehensive data cleaning (currency symbols, commas, spaces)
- Missing value handling
- Date parsing and validation
- 18-month historical coverage for trend analysis

## ⚡ Performance Optimizations

- **PDF Generation**: Fixed 400px chart heights for consistency
- **Page Breaks**: Strategic placement between major sections
- **Loading**: Async data loading with fallback sample data
- **Charts**: Optimized for both screen and print rendering

## 📞 Support

For questions or issues:
1. Check that all data files are present (`daily_sales.csv`, `regional_sales.csv`)
2. Ensure proper dependencies are installed
3. Verify HTML file opens correctly in browser before PDF generation

## 🏆 Key Insights Format

- **Conservative Analysis**: Fact-based findings without unsupported correlations
- **Executive Ready**: Non-technical language with clear business implications
- **Actionable**: Specific recommendations with quantified impact
- **Trend Focused**: WoW and MoM comparisons for all key metrics