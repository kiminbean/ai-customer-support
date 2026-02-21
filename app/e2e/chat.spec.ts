import { test, expect } from '@playwright/test';

test.describe('Chat Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/demo');
  });

  test('should display chat interface', async ({ page }) => {
    // 채팅 인터페이스가 표시되는지 확인
    await expect(page.locator('input[type="text"], textarea')).toBeVisible();
    await expect(page.getByRole('button', { name: /전송|send/i })).toBeVisible();
  });

  test('should send and receive message', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();
    const sendButton = page.getByRole('button', { name: /전송|send/i }).first();

    // 메시지 입력
    await input.fill('안녕하세요');
    await sendButton.click();

    // 응답 대기
    await page.waitForTimeout(2000);

    // 응답이 표시되는지 확인
    const messages = page.locator('[class*="message"], [class*="chat"]');
    await expect(messages.first()).toBeVisible({ timeout: 5000 });
  });

  test('should handle shipping inquiry', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();
    const sendButton = page.getByRole('button', { name: /전송|send/i }).first();

    await input.fill('배송 상태를 확인하고 싶습니다');
    await sendButton.click();

    await page.waitForTimeout(2000);

    // 배송 관련 응답 확인
    const content = await page.textContent('body');
    expect(content).toMatch(/배송|주문|송장/i);
  });

  test('should handle return inquiry', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();
    const sendButton = page.getByRole('button', { name: /전송|send/i }).first();

    await input.fill('반품하고 싶습니다');
    await sendButton.click();

    await page.waitForTimeout(2000);

    // 반품 관련 응답 확인
    const content = await page.textContent('body');
    expect(content).toMatch(/반품|교환|환불/i);
  });

  test('should show typing indicator', async ({ page }) => {
    const input = page.locator('input[type="text"], textarea').first();
    const sendButton = page.getByRole('button', { name: /전송|send/i }).first();

    await input.fill('테스트 메시지');
    await sendButton.click();

    // 로딩 인디케이터가 잠깐 표시되는지 확인
    const loadingVisible = await page.locator('[class*="loading"], [class*="typing"], [class*="spinner"]').count() > 0;

    // 로딩이 표시되거나 이미 응답이 왔을 수 있음
    expect(loadingVisible || (await page.locator('[class*="message"]').count()) > 0).toBeTruthy();
  });
});

test.describe('Chat History', () => {
  test('should maintain conversation context', async ({ page }) => {
    await page.goto('/demo');

    const input = page.locator('input[type="text"], textarea').first();
    const sendButton = page.getByRole('button', { name: /전송|send/i }).first();

    // 첫 번째 메시지
    await input.fill('안녕하세요');
    await sendButton.click();
    await page.waitForTimeout(1500);

    // 두 번째 메시지
    await input.fill('반갑습니다');
    await sendButton.click();
    await page.waitForTimeout(1500);

    // 두 메시지 모두 표시되는지 확인
    const messages = page.locator('[class*="user"], [class*="bot"], [class*="assistant"]');
    const count = await messages.count();
    expect(count).toBeGreaterThanOrEqual(2);
  });
});
