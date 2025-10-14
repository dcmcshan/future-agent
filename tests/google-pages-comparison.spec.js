const { test, expect } = require('@playwright/test');

test.describe('Google Pages Style Comparison', () => {
  test('should load the Google Pages comparison page successfully', async ({ page }) => {
    await page.goto('/google-pages-comparison.html');
    
    // Check page title
    await expect(page).toHaveTitle(/Future4200 vs Future-Agent Search/);
    
    // Check main heading
    await expect(page.locator('.logo h1')).toContainText('Future Search Comparison');
    
    // Check search box is present
    const searchBox = page.locator('#searchInput');
    await expect(searchBox).toBeVisible();
    await expect(searchBox).toHaveAttribute('placeholder', 'Search cannabis questions...');
  });

  test('should display two-column layout', async ({ page }) => {
    await page.goto('/google-pages-comparison.html');
    
    // Check comparison header
    await expect(page.locator('#future4200Header')).toContainText('Future4200 Forum');
    await expect(page.locator('#futureAgentHeader')).toContainText('Future-Agent AI');
    
    // Check results container has two columns
    const resultsContainer = page.locator('.results-container');
    await expect(resultsContainer).toBeVisible();
    
    // Check both result columns are present
    await expect(page.locator('#future4200Results')).toBeVisible();
    await expect(page.locator('#futureAgentResults')).toBeVisible();
  });

  test('should show empty states initially', async ({ page }) => {
    await page.goto('/google-pages-comparison.html');
    
    // Check empty states are displayed
    await expect(page.locator('#future4200Results .empty-state')).toBeVisible();
    await expect(page.locator('#futureAgentResults .empty-state')).toBeVisible();
    
    // Check empty state messages
    await expect(page.locator('#future4200Results .empty-state')).toContainText('Enter a search query to find Future4200 forum discussions');
    await expect(page.locator('#futureAgentResults .empty-state')).toContainText('Enter a search query to get Future-Agent AI responses');
  });

  test('should show search suggestions on input', async ({ page }) => {
    await page.goto('/google-pages-comparison.html');
    
    const searchBox = page.locator('#searchInput');
    
    // Type in search box
    await searchBox.fill('extraction');
    await page.waitForTimeout(500);
    
    // Check suggestions appear
    const suggestions = page.locator('.search-suggestions');
    await expect(suggestions).toBeVisible();
    
    // Check suggestion items
    const suggestionItems = suggestions.locator('.suggestion-item');
    await expect(suggestionItems).toHaveCount.greaterThan(0);
  });

  test('should perform search and show results', async ({ page }) => {
    await page.goto('/google-pages-comparison.html');
    
    const searchBox = page.locator('#searchInput');
    
    // Perform search
    await searchBox.fill('cannabis extraction');
    await searchBox.press('Enter');
    
    // Wait for loading states
    await page.waitForSelector('.loading-state', { timeout: 10000 });
    
    // Wait for results to load
    await page.waitForSelector('.result-item', { timeout: 15000 });
    
    // Check that results are displayed
    const future4200Results = page.locator('#future4200Results .result-item');
    const futureAgentResults = page.locator('#futureAgentResults .result-item');
    
    await expect(future4200Results).toHaveCount.greaterThan(0);
    await expect(futureAgentResults).toHaveCount.greaterThan(0);
    
    // Check result structure
    const firstResult = future4200Results.first();
    await expect(firstResult.locator('.result-title')).toBeVisible();
    await expect(firstResult.locator('.result-snippet')).toBeVisible();
    await expect(firstResult.locator('.result-meta')).toBeVisible();
  });

  test('should update result counts in headers', async ({ page }) => {
    await page.goto('/google-pages-comparison.html');
    
    const searchBox = page.locator('#searchInput');
    
    // Perform search
    await searchBox.fill('cannabis business');
    await searchBox.press('Enter');
    
    // Wait for results to load
    await page.waitForSelector('.result-item', { timeout: 15000 });
    
    // Check that counts are updated
    await expect(page.locator('#future4200Count')).not.toContainText('0 results');
    await expect(page.locator('#futureAgentCount')).not.toContainText('0 results');
  });

  test('should show stats bar after search', async ({ page }) => {
    await page.goto('/google-pages-comparison.html');
    
    const searchBox = page.locator('#searchInput');
    
    // Perform search
    await searchBox.fill('LED lights');
    await searchBox.press('Enter');
    
    // Wait for stats bar to appear
    await page.waitForSelector('#statsBar', { timeout: 10000 });
    
    // Check stats bar is visible
    await expect(page.locator('#statsBar')).toBeVisible();
    await expect(page.locator('#searchStats')).toBeVisible();
    await expect(page.locator('#searchTime')).toBeVisible();
  });

  test('should display confidence badges for Future-Agent results', async ({ page }) => {
    await page.goto('/google-pages-comparison.html');
    
    const searchBox = page.locator('#searchInput');
    
    // Perform search
    await searchBox.fill('distillation equipment');
    await searchBox.press('Enter');
    
    // Wait for results to load
    await page.waitForSelector('.result-item', { timeout: 15000 });
    
    // Check confidence badges in Future-Agent results
    const confidenceBadges = page.locator('#futureAgentResults .confidence-badge');
    await expect(confidenceBadges).toHaveCount.greaterThan(0);
    
    // Check badge content
    const firstBadge = confidenceBadges.first();
    await expect(firstBadge).toContainText('% confidence');
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/google-pages-comparison.html');
    
    // Check that search box is still visible
    await expect(page.locator('#searchInput')).toBeVisible();
    
    // Check that results container stacks on mobile
    const resultsContainer = page.locator('.results-container');
    const gridStyle = await resultsContainer.evaluate(el => getComputedStyle(el).gridTemplateColumns);
    expect(gridStyle).toBe('1fr');
    
    // Check comparison header stacks on mobile
    const comparisonHeader = page.locator('.comparison-header');
    const flexDirection = await comparisonHeader.evaluate(el => getComputedStyle(el).flexDirection);
    expect(flexDirection).toBe('column');
  });

  test('should handle search suggestions interaction', async ({ page }) => {
    await page.goto('/google-pages-comparison.html');
    
    const searchBox = page.locator('#searchInput');
    
    // Type to trigger suggestions
    await searchBox.fill('extraction');
    await page.waitForTimeout(500);
    
    // Check suggestions are visible
    const suggestions = page.locator('.search-suggestions');
    await expect(suggestions).toBeVisible();
    
    // Click on first suggestion
    const firstSuggestion = suggestions.locator('.suggestion-item').first();
    await firstSuggestion.click();
    
    // Check that search is performed
    await page.waitForSelector('.result-item', { timeout: 15000 });
    
    // Check that suggestions are hidden
    await expect(suggestions).not.toBeVisible();
  });

  test('should show loading states during search', async ({ page }) => {
    await page.goto('/google-pages-comparison.html');
    
    const searchBox = page.locator('#searchInput');
    
    // Perform search
    await searchBox.fill('cannabis cultivation');
    await searchBox.press('Enter');
    
    // Check loading states appear
    await expect(page.locator('#future4200Results .loading-state')).toBeVisible();
    await expect(page.locator('#futureAgentResults .loading-state')).toBeVisible();
    
    // Check loading spinner
    await expect(page.locator('.loading-spinner')).toHaveCount(2);
  });

  test('should handle empty search results', async ({ page }) => {
    await page.goto('/google-pages-comparison.html');
    
    const searchBox = page.locator('#searchInput');
    
    // Perform search with unlikely query
    await searchBox.fill('xyz123nonexistent');
    await searchBox.press('Enter');
    
    // Wait for results to load
    await page.waitForTimeout(2000);
    
    // Check that empty states are shown
    await expect(page.locator('#future4200Results .empty-state')).toBeVisible();
    await expect(page.locator('#futureAgentResults .empty-state')).toBeVisible();
  });
});