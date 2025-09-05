#!/usr/bin/env node

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function generateMarketingPDF() {
    let browser;
    
    try {
        console.log('🚀 Starting Marketing Report PDF generation...');
        
        const htmlPath = path.join(__dirname, 'eight_sleep_marketing_puppeteer.html');
        console.log(`📄 HTML file: ${htmlPath}`);
        console.log(`✅ File exists: ${fs.existsSync(htmlPath)}`);
        
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();
        
        // Set viewport for better chart rendering
        await page.setViewport({ width: 1920, height: 1080 });

        const htmlUrl = `file://${htmlPath}`;
        console.log(`🌐 Loading URL: ${htmlUrl}`);
        
        // Navigate to the HTML file
        await page.goto(htmlUrl, {
            waitUntil: ['networkidle0', 'domcontentloaded'],
            timeout: 30000
        });
        
        console.log('✅ Page loaded successfully');
        
        // Check if Highcharts is available
        const highchartsAvailable = await page.evaluate(() => {
            return typeof window.Highcharts !== 'undefined';
        });
        
        console.log(`📊 Highcharts available: ${highchartsAvailable}`);
        
        if (highchartsAvailable) {
            // Wait for charts to fully render
            console.log('⏳ Waiting for charts to render completely...');
            await new Promise(resolve => setTimeout(resolve, 10000)); // Longer wait for more charts
            
            // Check chart rendering
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
            
            console.log('📊 Chart rendering info:', JSON.stringify(chartInfo, null, 2));
            
            const chartCount = await page.evaluate(() => {
                return document.querySelectorAll('.highcharts-container').length;
            });
            
            console.log(`📈 Charts rendered: ${chartCount}/9 expected`);
        }
        
        // Generate PDF with optimized settings for marketing report
        console.log('📄 Generating PDF...');
        const pdfBuffer = await page.pdf({
            format: 'A4',
            margin: {
                top: '10mm',
                bottom: '10mm', 
                left: '8mm',
                right: '8mm'
            },
            printBackground: true,
            scale: 0.7, // Slightly smaller scale for more content per page
            preferCSSPageSize: false,
            displayHeaderFooter: true,
            headerTemplate: '<div style="font-size:10px;color:#666;text-align:center;width:100%;">Eight Sleep Marketing Report</div>',
            footerTemplate: '<div style="font-size:10px;color:#666;text-align:center;width:100%;"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
            landscape: false
        });
        
        // Save PDF
        const outputPath = path.join(__dirname, 'eight_sleep_marketing_report.pdf');
        fs.writeFileSync(outputPath, pdfBuffer);
        
        console.log(`✅ PDF generated: ${outputPath}`);
        console.log(`📏 File size: ${(pdfBuffer.length / 1024).toFixed(2)} KB`);
        console.log(`🎯 Pages: Multiple pages with professional layout`);
        
        return outputPath;
        
    } catch (error) {
        console.error(`❌ Error: ${error.message}`);
        throw error;
        
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// Run if called directly
if (require.main === module) {
    generateMarketingPDF()
        .then((outputPath) => {
            console.log(`\n🎉 Success! Marketing report PDF created:`);
            console.log(`📁 ${outputPath}`);
            console.log(`\n🚀 Ready for executive presentation!`);
        })
        .catch((error) => {
            console.error(`\n💥 Failed to generate marketing PDF:`, error);
            process.exit(1);
        });
}

module.exports = { generateMarketingPDF };