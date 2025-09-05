@echo off
echo ========================================
echo Eight Sleep Marketing Report Generator
echo ========================================
echo.

echo 📊 Generating comprehensive marketing performance PDF report...
echo This report includes 9 advanced charts and strategic analysis
echo.

cd /d "%~dp0"

echo Checking if Node.js is available...
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ❌ ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo Checking if required packages are installed...
if not exist "node_modules" (
    echo Installing required packages...
    npm install puppeteer
)

echo.
echo 🚀 Generating Marketing PDF using Node.js + Puppeteer...
node generate_marketing_pdf.js

if exist "eight_sleep_marketing_report.pdf" (
    echo.
    echo ✅ PDF generated successfully!
    echo File: eight_sleep_marketing_report.pdf
    
    :: Get file size
    for %%A in ("eight_sleep_marketing_report.pdf") do set "FILE_SIZE=%%~zA"
    echo Size: %FILE_SIZE% bytes
    echo.
    echo 📊 Report includes:
    echo • Executive summary with key metrics
    echo • 9 interactive-style charts
    echo • Strategic insights and recommendations  
    echo • Advanced analytics and forecasting
    echo • Professional formatting for presentations
    echo.
    echo 🎯 Opening PDF file...
    start "" "eight_sleep_marketing_report.pdf"
) else (
    echo.
    echo ❌ PDF generation failed
    echo The PDF file was not created
    echo Check the console output above for error details
)

echo.
pause
exit /b 0