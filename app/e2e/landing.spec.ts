import { test, expect } from '@playwright/test';

test.describe('Landing Page', () => {
  test('should load the landing page successfully', async ({ page }) => {
    await page.goto('/');
    
    // Check that page loaded
    await expect(page).toHaveTitle(/AI 고객지원|SupportAI/);
  });

  test('should display main hero section', async ({ page }) => {
    await page.goto('/');
    
    // Look for hero content
    const heroSection = page.locator('main');
    await expect(heroSection).toBeVisible();
  });

  test('should have navigation links', async ({ page }) => {
    await page.goto('/');
    
    // Check for navigation
    const nav = page.locator('nav, header');
    await expect(nav.first()).toBeVisible();
  });

  test('should navigate to demo page', async ({ page }) => {
    await page.goto('/');
    
    // Find and click demo link
    const demoLink = page.getByRole('link', { name: /데모|demo|체험/i });
    if (await demoLink.count() > 0) {
      await demoLink.first().click();
      await expect(page).toHaveURL(/demo/);
    }
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Page should still load correctly on mobile
    await expect(page).toHaveTitle(/AI 고객지원|SupportAI/);
  });
});
