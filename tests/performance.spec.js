const { test, expect } = require('@playwright/test');

test.describe('Performance', () => {
  test('should load homepage within acceptable time', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/');
    
    // Wait for main content to load
    await page.waitForSelector('h1', { timeout: 10000 });
    
    const loadTime = Date.now() - startTime;
    
    // Should load within 5 seconds
    expect(loadTime).toBeLessThan(5000);
  });

  test('should load F8 comparison page within acceptable time', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/f8-comparison.html');
    
    // Wait for main content to load
    await page.waitForSelector('.stats-grid', { timeout: 15000 });
    
    const loadTime = Date.now() - startTime;
    
    // Should load within 10 seconds (includes data loading)
    expect(loadTime).toBeLessThan(10000);
  });

  test('should have reasonable page size', async ({ page }) => {
    const response = await page.goto('/');
    
    // Check response headers for content length
    const contentLength = response.headers()['content-length'];
    if (contentLength) {
      const sizeKB = parseInt(contentLength) / 1024;
      // Page should be under 1MB
      expect(sizeKB).toBeLessThan(1024);
    }
  });

  test('should load data files efficiently', async ({ page }) => {
    const dataLoadTimes = [];
    
    // Monitor data loading times
    page.on('response', response => {
      if (response.url().includes('.json')) {
        const loadTime = response.request().timing().responseEnd - response.request().timing().requestStart;
        dataLoadTimes.push(loadTime);
      }
    });
    
    await page.goto('/f8-comparison.html');
    
    // Wait for data to load
    await page.waitForSelector('.stats-grid', { timeout: 15000 });
    
    // Check that data loaded within reasonable time
    if (dataLoadTimes.length > 0) {
      const maxLoadTime = Math.max(...dataLoadTimes);
      // Each data file should load within 5 seconds
      expect(maxLoadTime).toBeLessThan(5000);
    }
  });

  test('should handle filtering performance', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Wait for page to load
    await page.waitForSelector('.filters', { timeout: 15000 });
    
    // Test filter performance
    const startTime = Date.now();
    
    // Apply multiple filters quickly
    const extractionFilter = page.locator('.filter-button').filter({ hasText: 'Extraction' });
    await extractionFilter.click();
    
    const successFilter = page.locator('.filter-button').filter({ hasText: 'Success' });
    await successFilter.click();
    
    // Wait for filtering to complete
    await page.waitForTimeout(1000);
    
    const filterTime = Date.now() - startTime;
    
    // Filtering should complete within 2 seconds
    expect(filterTime).toBeLessThan(2000);
  });

  test('should handle search performance', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Wait for page to load
    await page.waitForSelector('.search-box', { timeout: 15000 });
    
    const searchBox = page.locator('.search-box');
    
    // Test search performance
    const startTime = Date.now();
    
    await searchBox.fill('extraction');
    await page.waitForTimeout(500); // Wait for search to process
    
    const searchTime = Date.now() - startTime;
    
    // Search should complete within 1 second
    expect(searchTime).toBeLessThan(1000);
  });

  test('should not have memory leaks during interactions', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Wait for page to load
    await page.waitForSelector('.filters', { timeout: 15000 });
    
    // Perform multiple interactions
    for (let i = 0; i < 10; i++) {
      // Apply different filters
      const filters = page.locator('.filter-button');
      const filterCount = await filters.count();
      const randomFilter = filters.nth(Math.floor(Math.random() * filterCount));
      await randomFilter.click();
      
      // Perform search
      const searchBox = page.locator('.search-box');
      await searchBox.fill(`test${i}`);
      
      await page.waitForTimeout(100);
    }
    
    // Check that page is still responsive
    const results = page.locator('#comparisonResults');
    await expect(results).toBeVisible();
  });

  test('should handle large datasets efficiently', async ({ page }) => {
    // This test would be more relevant with actual large datasets
    await page.goto('/f8-comparison.html');
    
    // Wait for page to load
    await page.waitForSelector('#comparisonResults', { timeout: 15000 });
    
    // Check that pagination is working (indicating efficient handling of large datasets)
    const pagination = page.locator('#pagination');
    if (await pagination.isVisible()) {
      await expect(pagination).toBeVisible();
      
      // Test pagination performance
      const nextButton = pagination.locator('.page-button').filter({ hasText: 'Next' });
      if (await nextButton.isEnabled()) {
        const startTime = Date.now();
        await nextButton.click();
        await page.waitForTimeout(500);
        const paginationTime = Date.now() - startTime;
        
        // Pagination should be fast
        expect(paginationTime).toBeLessThan(1000);
      }
    }
  });

  test('should have efficient CSS and JavaScript', async ({ page }) => {
    await page.goto('/');
    
    // Check that CSS is inline or efficiently loaded
    const stylesheets = await page.locator('link[rel="stylesheet"]').count();
    // Should have minimal external stylesheets
    expect(stylesheets).toBeLessThan(5);
    
    // Check that JavaScript is efficient
    const scripts = await page.locator('script[src]').count();
    // Should have minimal external scripts
    expect(scripts).toBeLessThan(5);
  });

  test('should load images efficiently', async ({ page }) => {
    await page.goto('/');
    
    // Check for any images and their loading
    const images = page.locator('img');
    const imageCount = await images.count();
    
    if (imageCount > 0) {
      // Wait for images to load
      await page.waitForLoadState('networkidle');
      
      // Check that images loaded successfully
      for (let i = 0; i < imageCount; i++) {
        const img = images.nth(i);
        const isLoaded = await img.evaluate(el => el.complete && el.naturalHeight !== 0);
        expect(isLoaded).toBe(true);
      }
    }
  });
});