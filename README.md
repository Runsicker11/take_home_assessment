# Eight Sleep Technical Assessment

This repository contains a comprehensive business analysis and automated WBR (Weekly Business Review) report generation system for Eight Sleep.

## 📊 Project Overview

The project demonstrates end-to-end data analysis, visualization, and report automation capabilities including:
- Customer Acquisition Cost (CAC) analysis and forecasting
- Regional performance tracking
- Member lifecycle revenue analysis  
- Automated PDF report generation

## 📁 Repository Structure

```
eight_sleep_assessment/
├── Raw Data/                           # Original data files
├── marketing_analysis/                 # Marketing funnel analysis
│   ├── marketing_performance.html    # Marketing Performance Dashboard
│   ├── eight_sleep_marketing_report.pdf # Final Marketing PDF Report
│   └── marketing_data.json          # Marketing metrics data
├── wbr/                               # WBR Report Generation System
│   ├── wbr_executive_report.html    # Interactive WBR Dashboard
│   ├── wbr_data.json                # Business metrics data
│   └── README.md                     # WBR documentation
└── README.md                          # This file
```

## 🎯 Main Deliverables

### 1. **WBR Executive Report** (`wbr/wbr_executive_report.html`)
- **Purpose**: Interactive Weekly Business Review dashboard for executive team
- **Features**: 
  - Real-time KPI tracking with WoW/MoM comparisons
  - CAC analysis with forecast scenarios
  - Regional performance metrics
  - Member lifecycle booking analysis
- **Access**: Open directly in browser for interactive experience

### 2. **Marketing Performance Dashboard** (`marketing_analysis/marketing_performance.html`)
- **Purpose**: Comprehensive marketing channel analysis and attribution insights
- **Features**:
  - Channel-by-channel ROAS and efficiency metrics
  - Attribution analysis across touchpoints
  - Customer journey mapping
  - PDF export capability via `eight_sleep_marketing_report.pdf`
- **Access**: Open directly in browser or view PDF report

## 🚀 WBR Report System

The `/wbr` folder contains a production-ready automated report generation system:

### Key Features:
- **📈 Interactive Charts**: 6 Highcharts visualizations with hover tooltips
- **💰 Smart Formatting**: Currency and number formatting (3.5M, $1,250)  
- **📝 Auto Commentary**: Data-driven insights generated automatically
- **🎯 Realistic Forecasting**: CAC scenarios based on historical performance
- **📄 Professional PDF**: High-quality PDF generation via Puppeteer
- **⚡ One-Click Generation**: Simple batch file execution

### Quick Start:
```bash
cd wbr
# Option 1: Use batch file (Windows)
generate_pdf_nodejs.bat

# Option 2: Direct execution
node test_pdf_simple.js
```

### Report Sections:
1. **Customer Acquisition Cost Analysis** - Weekly/monthly CAC trends with forecasting
2. **Regional Performance Overview** - Geographic breakdown with growth indicators  
3. **Member Lifecycle Analysis** - Upgrade vs renewal revenue patterns

## 📊 Key Business Insights

- **CAC Performance**: $793 average with ±15% natural volatility
- **Market Dominance**: US drives ~85% of total order volume
- **Growth Opportunities**: GB showing strongest growth (+15.8%)
- **Revenue Expansion**: Upgrade bookings represent significant upselling potential
- **Optimal Spend Strategy**: 20-30% increases provide best efficiency balance

## 🛠 Technical Stack

- **Frontend**: HTML5, CSS3, JavaScript
- **Charts**: Highcharts.js library
- **PDF Generation**: Node.js + Puppeteer
- **Data Format**: JSON
- **Analysis**: Python + Pandas (Jupyter notebooks)

## 📋 Requirements

### For PDF Generation:
- Node.js (v14+)  
- Puppeteer (`npm install puppeteer`)

### For Analysis:
- Python 3.8+
- Jupyter Notebook
- Pandas, NumPy

## 🎯 CAC Forecast Model

The forecasting model uses historical channel elasticity to project realistic scenarios:

| Spend Increase | Monthly Spend | Additional Spend | New CAC | CAC Increase |
|---------------|---------------|------------------|---------|--------------|
| +10% | $2.05M | +$186K/month | $825 | +4.0% |
| +20% | $2.23M | +$372K/month | $858 | +8.2% |
| +30% | $2.42M | +$558K/month | $895 | +12.9% |
| +50% | $2.79M | +$930K/month | $960 | +21.1% |
| +100% | $3.72M | +$1.86M/month | $1,190 | +50.1% |

**Methodology**: Based on observed market behavior with channel elasticity factor of 0.4 and diminishing returns at scale.

## 📈 Report Output

The generated PDF report includes:
- Executive KPI dashboard with WoW/MoM changes
- Interactive-style charts (rendered as high-quality images)
- Data-driven commentary with actionable insights
- Professional formatting optimized for executive consumption
- Clean page breaks and proper spacing

**Output**: `test_output.pdf` (564KB) - Professional quality business report

## 🔄 Automation Ready

The system is designed for easy automation:
- JSON data input (easily replaceable with API calls)
- Headless PDF generation
- Batch file execution
- No manual intervention required
- Consistent formatting and layout

## 📝 Documentation

- `wbr_analysis_reference.ipynb` - Comprehensive analysis methodology
- `README.md` files in each subdirectory
- Inline code comments and documentation

## 🎯 Business Value

This system demonstrates:
- **Executive Reporting**: Production-ready automated report generation
- **Data Analysis**: Sophisticated business metric analysis and forecasting  
- **Technical Execution**: Full-stack implementation with modern web technologies
- **Scalability**: Clean, maintainable code structure ready for production deployment
- **Business Acumen**: Realistic modeling based on market behavior and business constraints

---

*Generated for Eight Sleep Technical Assessment - Demonstrates end-to-end business analysis and automation capabilities.*