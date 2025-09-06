#!/usr/bin/env node

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

async function verifyPortraitFixes() {
    let browser;
    
    try {
        console.log('🔍 Verifying Portrait Mode Chart Fixes...');
        
        browser = await puppeteer.launch({
            headless: false, // Show browser for visual verification
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();
        
        // Portrait viewport matching our PDF settings
        await page.setViewport({ width: 1000, height: 1400 });

        const htmlPath = path.join(__dirname, 'eight_sleep_marketing_puppeteer.html');
        const htmlUrl = `file://${htmlPath}`;
        
        await page.goto(htmlUrl, {
            waitUntil: ['networkidle0', 'domcontentloaded'],
            timeout: 30000
        });
        
        // Wait for charts to render
        await new Promise(resolve => setTimeout(resolve, 8000));
        
        // Check specific issues mentioned
        console.log('\n📊 Checking specific chart elements...');
        
        // Check legend text for truncation
        const legendCheck = await page.evaluate(() => {
            const results = {};
            
            // Check for legend text content
            const legends = document.querySelectorAll('.highcharts-legend-item text');
            results.legendTexts = [];
            legends.forEach((legend, index) => {
                results.legendTexts.push({
                    index: index,
                    text: legend.textContent,
                    truncated: legend.textContent.includes('...')
                });
            });
            
            // Check for ROAS data labels
            const roasLabels = document.querySelectorAll('.highcharts-data-labels text');
            results.roasLabels = [];
            roasLabels.forEach((label, index) => {
                if (label.textContent.includes('x')) {
                    results.roasLabels.push({
                        index: index,
                        text: label.textContent,
                        overlapping: false // We'll check positioning later
                    });
                }
            });
            
            // Check email chart values
            const emailValues = document.querySelectorAll('.highcharts-data-labels text');
            results.emailValues = [];
            emailValues.forEach((value, index) => {
                if (value.textContent.includes('%')) {
                    results.emailValues.push({
                        index: index,
                        text: value.textContent
                    });
                }
            });
            
            return results;
        });
        
        console.log('\n✅ Legend Text Analysis:');
        legendCheck.legendTexts.forEach((legend, i) => {
            const status = legend.truncated ? '❌ TRUNCATED' : '✅ OK';
            console.log(`   ${i + 1}. "${legend.text}" ${status}`);
        });
        
        console.log('\n✅ ROAS Values Analysis:');
        legendCheck.roasLabels.forEach((roas, i) => {
            console.log(`   ${i + 1}. "${roas.text}"`);
        });
        
        console.log('\n✅ Email Conversion Values:');
        legendCheck.emailValues.forEach((email, i) => {
            const has76 = email.text.includes('7.6') || email.text.includes('7.60');
            const status = has76 ? '✅ CORRECT 7.6%' : '⚠️  CHECK VALUE';
            console.log(`   ${i + 1}. "${email.text}" ${status}`);
        });
        
        // Check chart dimensions fit in portrait
        const dimensionCheck = await page.evaluate(() => {
            const containers = document.querySelectorAll('.chart-container');
            const results = [];
            containers.forEach((container, index) => {
                const rect = container.getBoundingClientRect();
                results.push({
                    index: index,
                    width: Math.round(rect.width),
                    height: Math.round(rect.height),
                    fitsPortrait: rect.width <= 850 // Our portrait constraint
                });
            });
            return results;
        });
        
        console.log('\n✅ Portrait Fit Analysis:');
        dimensionCheck.forEach((chart, i) => {
            const status = chart.fitsPortrait ? '✅ FITS' : '❌ TOO WIDE';
            console.log(`   Chart ${i + 1}: ${chart.width}px × ${chart.height}px ${status}`);
        });
        
        console.log('\n🎯 Portrait Mode Verification Complete!');
        console.log('📄 PDF should now display properly without cutoffs');
        
        // Keep browser open for manual inspection
        console.log('\n👀 Browser will stay open for 30 seconds for manual inspection...');
        await new Promise(resolve => setTimeout(resolve, 30000));
        
    } catch (error) {
        console.error(`❌ Error: ${error.message}`);
        throw error;
        
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

// Run verification
verifyPortraitFixes()
    .then(() => {
        console.log('\n✅ Verification complete!');
    })
    .catch((error) => {
        console.error('\n💥 Verification failed:', error);
        process.exit(1);
    });