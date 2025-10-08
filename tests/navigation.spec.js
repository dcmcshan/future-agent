const { test, expect } = require('@playwright/test');

test.describe('Navigation', () => {
  test('should navigate between pages correctly', async ({ page }) => {
    // Start at homepage
    await page.goto('/');
    await expect(page).toHaveURL('/');
    
    // Navigate to F8 comparison page
    await page.click('a[href="f8-comparison.html"]');
    await expect(page).toHaveURL('/f8-comparison.html');
    await expect(page.locator('h1')).toContainText('F8 vs Future4200 Comparison');
    
    // Navigate back to homepage
    await page.click('a[href="index.html"]');
    await expect(page).toHaveURL('/');
    await expect(page.locator('h1')).toContainText('Future Agent');
  });

  test('should have consistent navigation across pages', async ({ page }) => {
    // Test homepage navigation
    await page.goto('/');
    const homeNav = page.locator('.nav a');
    await expect(homeNav).toHaveCount(2);
    await expect(homeNav.nth(0)).toHaveText('Home');
    await expect(homeNav.nth(1)).toHaveText('F8 Comparison');
    
    // Test F8 comparison page navigation
    await page.goto('/f8-comparison.html');
    const comparisonNav = page.locator('.nav a');
    await expect(comparisonNav).toHaveCount(2);
    await expect(comparisonNav.nth(0)).toHaveText('Home');
    await expect(comparisonNav.nth(1)).toHaveText('F8 Comparison');
  });

  test('should highlight active page in navigation', async ({ page }) => {
    // Test homepage active state
    await page.goto('/');
    const homeLink = page.locator('.nav a[href="index.html"]');
    await expect(homeLink).toHaveClass(/active/);
    
    // Test F8 comparison page active state
    await page.goto('/f8-comparison.html');
    const comparisonLink = page.locator('.nav a[href="f8-comparison.html"]');
    await expect(comparisonLink).toHaveClass(/active/);
  });

  test('should have working hover effects on navigation', async ({ page }) => {
    await page.goto('/');
    
    const navLinks = page.locator('.nav a');
    
    // Test hover effect on first link
    await navLinks.nth(0).hover();
    await expect(navLinks.nth(0)).toHaveCSS('color', 'rgb(201, 209, 217)'); // #c9d1d9
    
    // Test hover effect on second link
    await navLinks.nth(1).hover();
    await expect(navLinks.nth(1)).toHaveCSS('color', 'rgb(201, 209, 217)'); // #c9d1d9
  });

  test('should work with keyboard navigation', async ({ page }) => {
    await page.goto('/');
    
    // Tab to first navigation link
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Check if focus is on navigation
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
    
    // Press Enter to navigate
    await page.keyboard.press('Enter');
    await expect(page).toHaveURL('/f8-comparison.html');
  });

  test('should maintain navigation state during page interactions', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Wait for page to load
    await page.waitForSelector('.filters', { timeout: 10000 });
    
    // Interact with filters
    const searchBox = page.locator('.search-box');
    await searchBox.fill('test');
    
    // Check that navigation is still visible and functional
    const nav = page.locator('.nav');
    await expect(nav).toBeVisible();
    
    // Test navigation still works
    await page.click('a[href="index.html"]');
    await expect(page).toHaveURL('/');
  });
});