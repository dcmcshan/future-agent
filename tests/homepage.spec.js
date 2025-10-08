const { test, expect } = require('@playwright/test');

test.describe('Homepage', () => {
  test('should load the homepage successfully', async ({ page }) => {
    await page.goto('/');
    
    // Check page title
    await expect(page).toHaveTitle(/Future Agent/);
    
    // Check main heading
    await expect(page.locator('h1')).toContainText('Future Agent');
    
    // Check subtitle
    await expect(page.locator('.header p')).toContainText('Cannabis Industry Knowledge Agent');
  });

  test('should display statistics correctly', async ({ page }) => {
    await page.goto('/');
    
    // Check stats grid is visible
    await expect(page.locator('.stats-grid')).toBeVisible();
    
    // Check specific stat numbers
    await expect(page.locator('.stat-number').first()).toContainText('16,337');
    await expect(page.locator('.stat-number').nth(1)).toContainText('1,456');
    await expect(page.locator('.stat-number').nth(2)).toContainText('581');
    await expect(page.locator('.stat-number').nth(3)).toContainText('663');
  });

  test('should have working navigation', async ({ page }) => {
    await page.goto('/');
    
    // Check navigation links
    const navLinks = page.locator('.nav a');
    await expect(navLinks).toHaveCount(2);
    
    // Check F8 Comparison link
    await expect(navLinks.nth(1)).toHaveText('F8 Comparison');
    await expect(navLinks.nth(1)).toHaveAttribute('href', 'f8-comparison.html');
  });

  test('should have call-to-action section', async ({ page }) => {
    await page.goto('/');
    
    // Check CTA section
    await expect(page.locator('.cta-section')).toBeVisible();
    await expect(page.locator('.cta-section h3')).toContainText('Ready to Explore F8 vs Future4200 Comparison?');
    
    // Check CTA button
    const ctaButton = page.locator('.cta-button');
    await expect(ctaButton).toBeVisible();
    await expect(ctaButton).toHaveText('View F8 Comparison');
    await expect(ctaButton).toHaveAttribute('href', 'f8-comparison.html');
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Check that content is still visible on mobile
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('.stats-grid')).toBeVisible();
    await expect(page.locator('.features')).toBeVisible();
  });

  test('should have proper meta tags', async ({ page }) => {
    await page.goto('/');
    
    // Check viewport meta tag
    await expect(page.locator('meta[name="viewport"]')).toHaveAttribute('content', 'width=device-width, initial-scale=1.0');
    
    // Check charset
    await expect(page.locator('meta[charset="UTF-8"]')).toBeAttached();
  });
});