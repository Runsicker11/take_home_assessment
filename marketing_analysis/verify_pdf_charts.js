#!/usr/bin/env node

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function verifyPDFCharts() {
    let browser;
    
    try {
        console.log('🔍 Verifying PDF chart display quality...');
        
        const htmlPath = path.join(__dirname, 'eight_sleep_marketing_puppeteer.html');
        
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();
        
        // Set the same viewport as PDF generation
        await page.setViewport({ width: 1600, height: 1200 });

        const htmlUrl = `file://${htmlPath}`;
        await page.goto(htmlUrl, {
            waitUntil: ['networkidle0', 'domcontentloaded'],
            timeout: 30000
        });
        
        console.log('✅ Page loaded for verification');
        
        // Wait for charts to render
        await new Promise(resolve => setTimeout(resolve, 10000));
        
        // Check chart elements for potential cutoff issues
        const chartAnalysis = await page.evaluate(() => {
            const results = [];
            const containers = document.querySelectorAll('.highcharts-container');
            
            containers.forEach((container, index) => {
                const rect = container.getBoundingClientRect();
                const svg = container.querySelector('svg');
                const legends = container.querySelectorAll('.highcharts-legend-item');
                const xAxisLabels = container.querySelectorAll('.highcharts-xaxis-labels text');
                const yAxisLabels = container.querySelectorAll('.highcharts-yaxis-labels text');
                
                // Check if any elements are positioned outside visible area
                let hasOffscreenElements = false;
                const allTexts = container.querySelectorAll('text');
                allTexts.forEach(text => {
                    const textRect = text.getBoundingClientRect();
                    if (textRect.right > rect.right || textRect.left < rect.left) {
                        hasOffscreenElements = true;
                    }
                });
                
                results.push({
                    chartIndex: index,
                    containerWidth: rect.width,
                    containerHeight: rect.height,
                    legendCount: legends.length,
                    xAxisLabelsCount: xAxisLabels.length,
                    yAxisLabelsCount: yAxisLabels.length,
                    hasOffscreenElements,
                    chartId: container.parentElement?.id || 'unknown'
                });
            });
            
            return results;
        });
        
        console.log('\n📊 Chart Analysis Results:');
        console.log('='.repeat(50));
        
        chartAnalysis.forEach((chart, index) => {
            console.log(`\nChart ${index + 1} (${chart.chartId}):`);
            console.log(`  Dimensions: ${chart.containerWidth}x${chart.containerHeight}px`);
            console.log(`  Legend Items: ${chart.legendCount}`);
            console.log(`  X-Axis Labels: ${chart.xAxisLabelsCount}`);
            console.log(`  Y-Axis Labels: ${chart.yAxisLabelsCount}`);
            console.log(`  Has Cutoff Issues: ${chart.hasOffscreenElements ? '❌ YES' : '✅ NO'}`);
        });
        
        // Test with landscape PDF dimensions
        console.log('\n🧪 Testing with landscape PDF simulation...');
        
        // A4 landscape at 75% scale: roughly 1120px width available for content
        const pdfContentWidth = 1120;
        await page.setViewport({ width: pdfContentWidth, height: 800 });
        
        // Wait for resize
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        const landscapeAnalysis = await page.evaluate(() => {
            const containers = document.querySelectorAll('.highcharts-container');
            const results = [];
            
            containers.forEach((container, index) => {
                const rect = container.getBoundingClientRect();
                const allTexts = container.querySelectorAll('text');
                let maxTextRight = 0;
                let minTextLeft = Infinity;
                
                allTexts.forEach(text => {
                    const textRect = text.getBoundingClientRect();
                    maxTextRight = Math.max(maxTextRight, textRect.right);
                    minTextLeft = Math.min(minTextLeft, textRect.left);
                });
                
                const contentFitsInPDF = maxTextRight <= rect.right && minTextLeft >= rect.left;
                
                results.push({
                    chartIndex: index,
                    containerWidth: rect.width,
                    contentFitsInPDF,
                    textOverflow: maxTextRight - rect.right
                });
            });
            
            return results;
        });
        
        console.log('\n📋 Landscape PDF Compatibility:');
        console.log('='.repeat(50));
        
        let allChartsCompatible = true;
        landscapeAnalysis.forEach((chart, index) => {
            const status = chart.contentFitsInPDF ? '✅ FITS' : '❌ CUTOFF';
            console.log(`Chart ${index + 1}: ${status} (width: ${chart.containerWidth}px)`);
            if (!chart.contentFitsInPDF) {
                allChartsCompatible = false;
                console.log(`  Text overflow: ${chart.textOverflow.toFixed(2)}px`);
            }
        });
        
        console.log('\n' + '='.repeat(50));
        if (allChartsCompatible) {
            console.log('🎉 ALL CHARTS COMPATIBLE WITH LANDSCAPE PDF!');
        } else {
            console.log('⚠️  Some charts may still have cutoff issues in PDF');
        }
        
        return allChartsCompatible;
        
    } catch (error) {
        console.error(`❌ Verification Error: ${error.message}`);
        throw error;
        
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// Run verification
if (require.main === module) {
    verifyPDFCharts()
        .then((success) => {
            if (success) {
                console.log(`\n🚀 Verification complete - PDF should display all charts properly!`);
                process.exit(0);
            } else {
                console.log(`\n⚠️  Verification indicates potential issues - manual PDF inspection recommended`);
                process.exit(1);
            }
        })
        .catch((error) => {
            console.error(`\n💥 Verification failed:`, error);
            process.exit(1);
        });
}

module.exports = { verifyPDFCharts };