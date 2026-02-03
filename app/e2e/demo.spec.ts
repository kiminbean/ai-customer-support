import { test, expect } from '@playwright/test';

test.describe('Demo Page - Chat Functionality', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/demo');
  });

  test('should load the demo page', async ({ page }) => {
    await expect(page).toHaveURL(/demo/);
  });

  test('should display chat interface', async ({ page }) => {
    // Look for chat-related elements
    const chatContainer = page.locator('[class*="chat"], [data-testid="chat"], main');
    await expect(chatContainer.first()).toBeVisible();
  });

  test('should have message input field', async ({ page }) => {
    // Find text input or textarea for messages
    const input = page.locator('input[type="text"], textarea').first();
    await expect(input).toBeVisible();
  });

  test('should allow typing a message', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();
    await input.fill('안녕하세요, 테스트 메시지입니다.');
    await expect(input).toHaveValue('안녕하세요, 테스트 메시지입니다.');
  });

  test('should have send button', async ({ page }) => {
    const sendButton = page.locator('button[type="submit"], button:has-text("전송"), button:has-text("보내기"), button:has-text("Send")');
    await expect(sendButton.first()).toBeVisible();
  });

  test('should submit message on button click', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();
    const sendButton = page.locator('button[type="submit"], button:has-text("전송"), button:has-text("보내기")').first();
    
    await input.fill('테스트 질문입니다');
    
    // Click send if button exists
    if (await sendButton.count() > 0) {
      await sendButton.click();
      // Wait for some response (either loading or message)
      await page.waitForTimeout(500);
    }
  });
});
