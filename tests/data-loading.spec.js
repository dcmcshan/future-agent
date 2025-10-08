const { test, expect } = require('@playwright/test');

test.describe('Data Loading', () => {
  test('should load F8 responses data successfully', async ({ page }) => {
    // Monitor network requests
    const responses = [];
    page.on('response', response => {
      if (response.url().includes('f8_responses_demo.json')) {
        responses.push(response);
      }
    });
    
    await page.goto('/f8-comparison.html');
    
    // Wait for data to load
    await page.waitForSelector('.stats-grid', { timeout: 15000 });
    
    // Check that data was loaded
    expect(responses.length).toBeGreaterThan(0);
    expect(responses[0].status()).toBe(200);
    
    // Check that stats are populated
    const statNumbers = page.locator('.stat-number');
    await expect(statNumbers.first()).not.toContainText('-');
  });

  test('should load processing statistics', async ({ page }) => {
    // Monitor network requests
    const responses = [];
    page.on('response', response => {
      if (response.url().includes('f8_processing_stats.json')) {
        responses.push(response);
      }
    });
    
    await page.goto('/f8-comparison.html');
    
    // Wait for stats to load
    await page.waitForSelector('.stats-grid', { timeout: 15000 });
    
    // Check that stats data was loaded
    expect(responses.length).toBeGreaterThan(0);
    expect(responses[0].status()).toBe(200);
    
    // Check that statistics are displayed
    const statsGrid = page.locator('.stats-grid');
    await expect(statsGrid).toBeVisible();
    
    // Check for specific stat labels
    await expect(page.locator('.stat-label').filter({ hasText: 'Total Questions' })).toBeVisible();
    await expect(page.locator('.stat-label').filter({ hasText: 'F8 Responses' })).toBeVisible();
  });

  test('should handle data loading errors gracefully', async ({ page }) => {
    // Intercept data requests and return errors
    await page.route('**/data/f8_responses_demo.json', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' })
      });
    });
    
    await page.route('**/data/f8_processing_stats.json', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Internal server error' })
      });
    });
    
    await page.goto('/f8-comparison.html');
    
    // Wait for error handling
    await page.waitForTimeout(5000);
    
    // Check that page still loads with fallback data
    const results = page.locator('#comparisonResults');
    await expect(results).toBeVisible();
    
    // Should show some content even with errors
    const content = await results.textContent();
    expect(content).toBeTruthy();
  });

  test('should show loading states during data fetch', async ({ page }) => {
    // Slow down network requests
    await page.route('**/data/*.json', async route => {
      await page.waitForTimeout(1000); // Simulate slow network
      await route.continue();
    });
    
    await page.goto('/f8-comparison.html');
    
    // Check that loading indicator appears
    const loadingIndicator = page.locator('#loading');
    // Note: Loading might be too fast to catch in some cases
    await expect(loadingIndicator).toBeAttached();
  });

  test('should populate comparison results with loaded data', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Wait for results to load
    await page.waitForSelector('#comparisonResults', { timeout: 15000 });
    
    // Check that comparison cards are populated
    const comparisonCards = page.locator('.comparison-card');
    if (await comparisonCards.count() > 0) {
      // Check for question content
      const questionText = page.locator('.question-text');
      await expect(questionText.first()).toBeVisible();
      
      // Check for F8 response content
      const f8Response = page.locator('h3').filter({ hasText: 'F8 LangChain Response' });
      await expect(f8Response).toBeVisible();
      
      // Check for community response content
      const communityResponse = page.locator('h3').filter({ hasText: 'Community Response' });
      await expect(communityResponse).toBeVisible();
      
      // Check for analysis content
      const analysis = page.locator('h3').filter({ hasText: 'Analysis' });
      await expect(analysis).toBeVisible();
    }
  });

  test('should handle empty data gracefully', async ({ page }) => {
    // Intercept data requests and return empty data
    await page.route('**/data/f8_responses_demo.json', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ results: [] })
      });
    });
    
    await page.goto('/f8-comparison.html');
    
    // Wait for page to process empty data
    await page.waitForTimeout(3000);
    
    // Check that page handles empty data gracefully
    const results = page.locator('#comparisonResults');
    await expect(results).toBeVisible();
    
    // Should show "No Results Found" or similar message
    const content = await results.textContent();
    expect(content.toLowerCase()).toMatch(/no results|empty|no data/);
  });

  test('should maintain data state during filtering', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Wait for data to load
    await page.waitForSelector('#comparisonResults', { timeout: 15000 });
    
    // Apply a filter
    const extractionFilter = page.locator('.filter-button').filter({ hasText: 'Extraction' });
    await extractionFilter.click();
    
    // Wait for filtering to complete
    await page.waitForTimeout(1000);
    
    // Check that data is still loaded and filtered
    const results = page.locator('#comparisonResults');
    await expect(results).toBeVisible();
    
    // Check that filter is active
    await expect(extractionFilter).toHaveClass(/active/);
  });

  test('should handle concurrent data requests', async ({ page }) => {
    const responses = [];
    page.on('response', response => {
      if (response.url().includes('.json')) {
        responses.push({
          url: response.url(),
          status: response.status()
        });
      }
    });
    
    await page.goto('/f8-comparison.html');
    
    // Wait for all requests to complete
    await page.waitForSelector('.stats-grid', { timeout: 15000 });
    
    // Check that multiple data files were requested
    const dataRequests = responses.filter(r => r.url.includes('data/'));
    expect(dataRequests.length).toBeGreaterThan(0);
    
    // Check that all requests were successful
    const failedRequests = dataRequests.filter(r => r.status >= 400);
    expect(failedRequests.length).toBe(0);
  });
});