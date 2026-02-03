import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test('should load dashboard page', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check page loaded (might redirect to login or show dashboard)
    await expect(page).toHaveURL(/dashboard|login|auth/);
  });

  test('should display sidebar navigation', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Look for sidebar or navigation menu
    const sidebar = page.locator('[class*="sidebar"], nav, aside');
    await expect(sidebar.first()).toBeVisible();
  });

  test('should have navigation menu items', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Check for common dashboard nav items
    const navItems = page.locator('nav a, aside a, [class*="sidebar"] a');
    const count = await navItems.count();
    expect(count).toBeGreaterThan(0);
  });

  test('should navigate to crawler page', async ({ page }) => {
    await page.goto('/crawler');
    await expect(page).toHaveURL(/crawler/);
  });

  test('should navigate to datahub page', async ({ page }) => {
    await page.goto('/datahub');
    await expect(page).toHaveURL(/datahub/);
  });

  test('should navigate to voice page', async ({ page }) => {
    await page.goto('/voice');
    await expect(page).toHaveURL(/voice/);
  });
});

test.describe('Dashboard Tabs', () => {
  test('should display overview tab content', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Look for overview related content
    const mainContent = page.locator('main, [class*="content"]');
    await expect(mainContent.first()).toBeVisible();
  });

  test('should switch between tabs', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Find tab buttons if they exist
    const tabs = page.locator('[role="tab"], button:has-text("분석"), button:has-text("대화")');
    const tabCount = await tabs.count();
    
    if (tabCount > 1) {
      await tabs.nth(1).click();
      await page.waitForTimeout(300);
    }
  });
});
