#!/usr/bin/env node

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function testPDF() {
    let browser;
    
    try {
        console.log('Testing PDF generation...');
        
        const htmlPath = path.join(__dirname, 'wbr_report_puppeteer.html');
        console.log(`HTML file: ${htmlPath}`);
        console.log(`File exists: ${fs.existsSync(htmlPath)}`);
        
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();
        
        // Set viewport much larger for better chart rendering
        await page.setViewport({ width: 1920, height: 1080 });

        const htmlUrl = `file://${htmlPath}`;
        console.log(`Loading URL: ${htmlUrl}`);
        
        // Navigate to the HTML file
        await page.goto(htmlUrl, {
            waitUntil: ['networkidle0', 'domcontentloaded'],
            timeout: 30000
        });
        
        console.log('Page loaded successfully');
        
        // Check if Highcharts is available
        const highchartsAvailable = await page.evaluate(() => {
            return typeof window.Highcharts !== 'undefined';
        });
        
        console.log(`Highcharts available: ${highchartsAvailable}`);
        
        if (highchartsAvailable) {
            // Wait for charts to fully render with animations
            console.log('Waiting for charts to render completely...');
            await new Promise(resolve => setTimeout(resolve, 8000));
            
            // Check chart dimensions
            const chartInfo = await page.evaluate(() => {
                const containers = document.querySelectorAll('.highcharts-container');
                const results = [];
                containers.forEach((container, index) => {
                    const rect = container.getBoundingClientRect();
                    const svg = container.querySelector('svg');
                    results.push({
                        index,
                        width: rect.width,
                        height: rect.height,
                        hasSVG: !!svg,
                        svgChildren: svg ? svg.children.length : 0
                    });
                });
                return results;
            });
            
            console.log('Chart rendering info:', JSON.stringify(chartInfo, null, 2));
            
            const chartCount = await page.evaluate(() => {
                return document.querySelectorAll('.highcharts-container').length;
            });
            
            console.log(`Charts rendered: ${chartCount}`);
        }
        
        // Check if KPI data is populated
        const kpiCount = await page.evaluate(() => {
            return document.querySelectorAll('.kpi-card').length;
        });
        
        console.log(`KPI cards: ${kpiCount}`);
        
        // Generate PDF with settings optimized for wide charts
        console.log('Generating PDF...');
        const pdfBuffer = await page.pdf({
            format: 'A4',
            margin: {
                top: '5mm',
                bottom: '5mm', 
                left: '5mm',
                right: '5mm'
            },
            printBackground: true,
            scale: 0.75,
            preferCSSPageSize: false,
            displayHeaderFooter: false,
            landscape: false
        });
        
        // Save PDF
        const outputPath = path.join(__dirname, 'test_output.pdf');
        fs.writeFileSync(outputPath, pdfBuffer);
        
        console.log(`PDF generated: ${outputPath}`);
        console.log(`File size: ${(pdfBuffer.length / 1024).toFixed(2)} KB`);
        
    } catch (error) {
        console.error(`Error: ${error.message}`);
        
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

testPDF();