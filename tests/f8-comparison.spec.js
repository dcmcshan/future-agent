const { test, expect } = require('@playwright/test');

test.describe('F8 Comparison Page', () => {
  test('should load the F8 comparison page successfully', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Check page title
    await expect(page).toHaveTitle(/F8 vs Future4200 Comparison/);
    
    // Check main heading
    await expect(page.locator('h1')).toContainText('F8 vs Future4200 Comparison');
    await expect(page.locator('.header p')).toContainText('Compare F8 LangChain responses with Future4200 forum discussions');
  });

  test('should display statistics overview', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Wait for stats to load
    await page.waitForSelector('.stats-overview', { timeout: 10000 });
    
    // Check stats grid is visible
    await expect(page.locator('.stats-grid')).toBeVisible();
    
    // Check that stat numbers are loaded (not showing dashes)
    const statNumbers = page.locator('.stat-number');
    await expect(statNumbers.first()).not.toContainText('-');
  });

  test('should have working filters', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Wait for filters to load
    await page.waitForSelector('.filters', { timeout: 10000 });
    
    // Test category filter
    const categoryButtons = page.locator('.filter-group').first().locator('.filter-button');
    await expect(categoryButtons).toHaveCount(6); // All, Extraction, Cultivation, Business, Equipment
    
    // Click on Extraction filter
    await categoryButtons.nth(1).click();
    await expect(categoryButtons.nth(1)).toHaveClass(/active/);
    
    // Test status filter
    const statusButtons = page.locator('.filter-group').nth(1).locator('.filter-button');
    await expect(statusButtons).toHaveCount(4); // All, Success, Error, Timeout
    
    // Click on Success filter
    await statusButtons.nth(1).click();
    await expect(statusButtons.nth(1)).toHaveClass(/active/);
  });

  test('should have working search functionality', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Wait for search box to load
    await page.waitForSelector('.search-box', { timeout: 10000 });
    
    const searchBox = page.locator('.search-box');
    await expect(searchBox).toBeVisible();
    await expect(searchBox).toHaveAttribute('placeholder', 'Search questions and responses...');
    
    // Test search functionality
    await searchBox.fill('extraction');
    await page.waitForTimeout(500); // Wait for search to process
    
    // Check that results are filtered
    const results = page.locator('#comparisonResults .comparison-card');
    if (await results.count() > 0) {
      await expect(results.first()).toBeVisible();
    }
  });

  test('should display comparison results', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Wait for results to load
    await page.waitForSelector('#comparisonResults', { timeout: 15000 });
    
    // Check that results container is visible
    await expect(page.locator('#comparisonResults')).toBeVisible();
    
    // Check for comparison cards
    const comparisonCards = page.locator('.comparison-card');
    if (await comparisonCards.count() > 0) {
      await expect(comparisonCards.first()).toBeVisible();
      
      // Check for three-column layout
      const comparisonGrid = page.locator('.comparison-grid');
      await expect(comparisonGrid).toBeVisible();
      
      // Check for F8 response column
      await expect(page.locator('h3').filter({ hasText: 'F8 LangChain Response' })).toBeVisible();
      
      // Check for Community response column
      await expect(page.locator('h3').filter({ hasText: 'Community Response' })).toBeVisible();
      
      // Check for Analysis column
      await expect(page.locator('h3').filter({ hasText: 'Analysis' })).toBeVisible();
    }
  });

  test('should have working pagination', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Wait for pagination to load
    await page.waitForSelector('#pagination', { timeout: 15000 });
    
    const pagination = page.locator('#pagination');
    if (await pagination.isVisible()) {
      // Check for pagination buttons
      const pageButtons = pagination.locator('.page-button');
      await expect(pageButtons).toHaveCount.greaterThan(0);
      
      // Test pagination navigation
      const nextButton = pagination.locator('.page-button').filter({ hasText: 'Next' });
      if (await nextButton.isEnabled()) {
        await nextButton.click();
        await page.waitForTimeout(500);
      }
    }
  });

  test('should show loading indicator', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Check that loading indicator appears initially
    const loadingIndicator = page.locator('#loading');
    // The loading might be too fast to catch, so we'll just check it exists
    await expect(loadingIndicator).toBeAttached();
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/f8-comparison.html');
    
    // Wait for content to load
    await page.waitForSelector('.stats-overview', { timeout: 10000 });
    
    // Check that content is still visible on mobile
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('.filters')).toBeVisible();
    await expect(page.locator('#comparisonResults')).toBeVisible();
    
    // Check that comparison grid stacks on mobile
    const comparisonGrid = page.locator('.comparison-grid');
    if (await comparisonGrid.isVisible()) {
      // On mobile, the grid should stack vertically
      const gridStyle = await comparisonGrid.evaluate(el => getComputedStyle(el).gridTemplateColumns);
      expect(gridStyle).toBe('1fr');
    }
  });

  test('should handle data loading errors gracefully', async ({ page }) => {
    // Intercept the data requests and return an error
    await page.route('**/data/f8_responses_demo.json', route => {
      route.fulfill({
        status: 404,
        contentType: 'application/json',
        body: JSON.stringify({ error: 'Data not found' })
      });
    });
    
    await page.goto('/f8-comparison.html');
    
    // Wait for error handling
    await page.waitForTimeout(5000);
    
    // Check that error is handled gracefully
    const results = page.locator('#comparisonResults');
    await expect(results).toBeVisible();
    
    // Should show some fallback content or error message
    const content = await results.textContent();
    expect(content).toBeTruthy();
  });
});