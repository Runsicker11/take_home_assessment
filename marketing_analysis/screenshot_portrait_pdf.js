#!/usr/bin/env node

const puppeteer = require('puppeteer');
const path = require('path');

async function screenshotPortraitPDF() {
    let browser;
    
    try {
        console.log('📸 Taking screenshots of portrait optimized charts...');
        
        browser = await puppeteer.launch({
            headless: true,
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();
        
        // Portrait viewport matching our PDF
        await page.setViewport({ width: 1000, height: 1400 });

        const htmlPath = path.join(__dirname, 'eight_sleep_marketing_puppeteer.html');
        const htmlUrl = `file://${htmlPath}`;
        
        await page.goto(htmlUrl, {
            waitUntil: ['networkidle0', 'domcontentloaded'],
            timeout: 30000
        });
        
        // Wait for charts to render
        await new Promise(resolve => setTimeout(resolve, 8000));
        
        // Take full page screenshot
        const screenshotPath = path.join(__dirname, 'screenshots', 'portrait_mode_verification.png');
        await page.screenshot({
            path: screenshotPath,
            fullPage: true,
            type: 'png'
        });
        
        console.log(`📸 Screenshot saved: ${screenshotPath}`);
        
        // Take specific chart screenshots
        const chartContainers = await page.$$('.chart-container');
        
        for (let i = 0; i < chartContainers.length && i < 3; i++) {
            const chartPath = path.join(__dirname, 'screenshots', `chart_${i + 1}_portrait.png`);
            await chartContainers[i].screenshot({
                path: chartPath,
                type: 'png'
            });
            console.log(`📊 Chart ${i + 1} screenshot: ${chartPath}`);
        }
        
        console.log('\n✅ Portrait mode screenshots completed!');
        console.log('🎯 Charts should now display properly in PDF without cutoffs');
        
    } catch (error) {
        console.error(`❌ Error: ${error.message}`);
        throw error;
        
    } finally {
        if (browser) {
            await browser.close();
        }
    }
}

screenshotPortraitPDF()
    .then(() => {
        console.log('\n📸 Screenshots complete!');
    })
    .catch((error) => {
        console.error('\n💥 Screenshot failed:', error);
        process.exit(1);
    });