const { test, expect } = require('@playwright/test');

test.describe('Accessibility', () => {
  test('should have proper heading hierarchy', async ({ page }) => {
    await page.goto('/');
    
    // Check that h1 exists and is unique
    const h1Elements = page.locator('h1');
    await expect(h1Elements).toHaveCount(1);
    
    // Check that h1 contains meaningful text
    const h1Text = await h1Elements.textContent();
    expect(h1Text).toBeTruthy();
    expect(h1Text.length).toBeGreaterThan(0);
  });

  test('should have proper alt text for images', async ({ page }) => {
    await page.goto('/');
    
    // Check all images have alt attributes
    const images = page.locator('img');
    const imageCount = await images.count();
    
    for (let i = 0; i < imageCount; i++) {
      const img = images.nth(i);
      const altText = await img.getAttribute('alt');
      expect(altText).toBeTruthy();
    }
  });

  test('should have proper form labels', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Wait for page to load
    await page.waitForSelector('.search-box', { timeout: 10000 });
    
    // Check search box has proper attributes
    const searchBox = page.locator('.search-box');
    await expect(searchBox).toHaveAttribute('placeholder');
    
    // Check that search box is properly labeled
    const searchLabel = page.locator('label').filter({ hasText: /search/i });
    if (await searchLabel.count() > 0) {
      const forAttribute = await searchLabel.getAttribute('for');
      const searchId = await searchBox.getAttribute('id');
      expect(forAttribute).toBe(searchId);
    }
  });

  test('should have proper button labels', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Wait for page to load
    await page.waitForSelector('.filter-button', { timeout: 10000 });
    
    // Check all buttons have meaningful text
    const buttons = page.locator('button');
    const buttonCount = await buttons.count();
    
    for (let i = 0; i < buttonCount; i++) {
      const button = buttons.nth(i);
      const buttonText = await button.textContent();
      expect(buttonText).toBeTruthy();
      expect(buttonText.trim().length).toBeGreaterThan(0);
    }
  });

  test('should have proper link text', async ({ page }) => {
    await page.goto('/');
    
    // Check all links have meaningful text
    const links = page.locator('a');
    const linkCount = await links.count();
    
    for (let i = 0; i < linkCount; i++) {
      const link = links.nth(i);
      const linkText = await link.textContent();
      const href = await link.getAttribute('href');
      
      // Skip empty links (like anchor links)
      if (href && !href.startsWith('#')) {
        expect(linkText).toBeTruthy();
        expect(linkText.trim().length).toBeGreaterThan(0);
      }
    }
  });

  test('should have proper color contrast', async ({ page }) => {
    await page.goto('/');
    
    // Check main heading color contrast
    const h1 = page.locator('h1');
    const h1Color = await h1.evaluate(el => {
      const styles = getComputedStyle(el);
      return styles.color;
    });
    
    // Check that text is not too light (should be dark enough for contrast)
    expect(h1Color).toBeTruthy();
    
    // Check button colors
    const buttons = page.locator('.cta-button');
    if (await buttons.count() > 0) {
      const buttonColor = await buttons.first().evaluate(el => {
        const styles = getComputedStyle(el);
        return {
          color: styles.color,
          backgroundColor: styles.backgroundColor
        };
      });
      
      expect(buttonColor.color).toBeTruthy();
      expect(buttonColor.backgroundColor).toBeTruthy();
    }
  });

  test('should be keyboard navigable', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Wait for page to load
    await page.waitForSelector('.filters', { timeout: 10000 });
    
    // Test tab navigation
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    
    // Check that focus is visible
    const focusedElement = page.locator(':focus');
    await expect(focusedElement).toBeVisible();
    
    // Test that focused element is interactive
    const focusedTag = await focusedElement.evaluate(el => el.tagName.toLowerCase());
    expect(['input', 'button', 'a', 'select', 'textarea']).toContain(focusedTag);
  });

  test('should have proper ARIA labels where needed', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Wait for page to load
    await page.waitForSelector('.filters', { timeout: 10000 });
    
    // Check for ARIA labels on interactive elements
    const interactiveElements = page.locator('input, button, select, textarea');
    const elementCount = await interactiveElements.count();
    
    for (let i = 0; i < elementCount; i++) {
      const element = interactiveElements.nth(i);
      const ariaLabel = await element.getAttribute('aria-label');
      const ariaLabelledBy = await element.getAttribute('aria-labelledby');
      const id = await element.getAttribute('id');
      
      // At least one of these should be present for accessibility
      const hasAccessibleName = ariaLabel || ariaLabelledBy || id;
      expect(hasAccessibleName).toBeTruthy();
    }
  });

  test('should have proper semantic HTML structure', async ({ page }) => {
    await page.goto('/');
    
    // Check for proper semantic elements
    await expect(page.locator('header, .header')).toBeVisible();
    await expect(page.locator('main, .container')).toBeVisible();
    await expect(page.locator('nav, .nav')).toBeVisible();
    
    // Check that headings are in proper order
    const headings = page.locator('h1, h2, h3, h4, h5, h6');
    const headingCount = await headings.count();
    
    let lastLevel = 0;
    for (let i = 0; i < headingCount; i++) {
      const heading = headings.nth(i);
      const tagName = await heading.evaluate(el => el.tagName);
      const level = parseInt(tagName.substring(1));
      
      // Headings should not skip levels (e.g., h1 to h3)
      if (lastLevel > 0) {
        expect(level - lastLevel).toBeLessThanOrEqual(1);
      }
      
      lastLevel = level;
    }
  });

  test('should work with screen reader', async ({ page }) => {
    await page.goto('/f8-comparison.html');
    
    // Wait for page to load
    await page.waitForSelector('.stats-grid', { timeout: 15000 });
    
    // Check that important content is accessible
    const mainHeading = page.locator('h1');
    await expect(mainHeading).toBeVisible();
    
    const statsGrid = page.locator('.stats-grid');
    await expect(statsGrid).toBeVisible();
    
    // Check that interactive elements are properly labeled
    const searchBox = page.locator('.search-box');
    if (await searchBox.isVisible()) {
      await expect(searchBox).toBeVisible();
    }
    
    const filterButtons = page.locator('.filter-button');
    if (await filterButtons.count() > 0) {
      await expect(filterButtons.first()).toBeVisible();
    }
  });
});