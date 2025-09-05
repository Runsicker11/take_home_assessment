@echo off
echo ========================================
echo WBR Report PDF Generation (Node.js)
echo ========================================
echo.

echo This version uses Node.js + Puppeteer which handles charts better than browser printing
echo.

cd /d "%~dp0"

echo Checking if Node.js is available...
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Node.js is not installed or not in PATH
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
echo Generating PDF using Node.js...
node test_pdf_simple.js

if exist "test_output.pdf" (
    echo.
    echo ✅ PDF generated successfully!
    echo File: test_output.pdf
    
    :: Get file size
    for %%A in ("test_output.pdf") do set "FILE_SIZE=%%~zA"
    echo Size: %FILE_SIZE% bytes
    echo.
    echo Opening PDF file...
    start "" "test_output.pdf"
) else (
    echo.
    echo ❌ PDF generation failed
    echo The PDF file was not created
)

echo.
pause
exit /b 0