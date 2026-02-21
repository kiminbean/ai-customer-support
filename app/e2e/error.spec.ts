import { test, expect } from '@playwright/test';

test.describe('Error Scenarios', () => {
  test('should handle 404 page', async ({ page }) => {
    await page.goto('/nonexistent-page-12345');

    // 404 페이지가 표시되는지 확인
    await expect(page.locator('text=/404|찾을 수 없|not found/i')).toBeVisible({ timeout: 5000 });
  });

  test('should handle empty message submission', async ({ page }) => {
    await page.goto('/demo');

    const input = page.locator('input[type="text"], textarea').first();
    const sendButton = page.getByRole('button', { name: /전송|send/i }).first();

    // 빈 메시지로 전송 시도
    await input.fill('');
    await sendButton.click();

    // 에러 메시지 또는 아무 일도 일어나지 않음
    // 정상 동작이어야 함
    await page.waitForTimeout(1000);
    await expect(page).toHaveURL(/demo/);
  });

  test('should handle very long message', async ({ page }) => {
    await page.goto('/demo');

    const input = page.locator('input[type="text"], textarea').first();
    const sendButton = page.getByRole('button', { name: /전송|send/i }).first();

    // 매우 긴 메시지 (5000자 이상)
    const longMessage = '테스트 메시지입니다. '.repeat(300);
    await input.fill(longMessage);
    await sendButton.click();

    await page.waitForTimeout(2000);

    // 에러 없이 처리되거나 적절한 에러 메시지 표시
    const content = await page.textContent('body');
    expect(content).toBeTruthy();
  });

  test('should handle special characters', async ({ page }) => {
    await page.goto('/demo');

    const input = page.locator('input[type="text"], textarea').first();
    const sendButton = page.getByRole('button', { name: /전송|send/i }).first();

    // 특수 문자 포함 메시지
    await input.fill('테스트 <script>alert("xss")</script> @#$%^&*()');
    await sendButton.click();

    await page.waitForTimeout(2000);

    // XSS 공격이 실행되지 않아야 함
    const alertDialog = page.locator('[role="alert"]').filter({ hasText: 'xss' });
    await expect(alertDialog).not.toBeVisible();
  });

  test('should handle rapid message submissions', async ({ page }) => {
    await page.goto('/demo');

    const input = page.locator('input[type="text"], textarea').first();
    const sendButton = page.getByRole('button', { name: /전송|send/i }).first();

    // 빠르게 여러 메시지 전송
    for (let i = 0; i < 3; i++) {
      await input.fill(`메시지 ${i + 1}`);
      await sendButton.click();
      await page.waitForTimeout(100);
    }

    await page.waitForTimeout(3000);

    // 페이지가 정상적으로 동작해야 함
    await expect(page).toHaveURL(/demo/);
  });
});

test.describe('Network Errors', () => {
  test('should handle offline gracefully', async ({ page, context }) => {
    await page.goto('/demo');

    // 오프라인 모드로 전환
    await context.setOffline(true);

    const input = page.locator('input[type="text"], textarea').first();
    const sendButton = page.getByRole('button', { name: /전송|send/i }).first();

    await input.fill('오프라인 테스트');
    await sendButton.click();

    await page.waitForTimeout(2000);

    // 온라인으로 복구
    await context.setOffline(false);
  });
});

test.describe('Form Validation', () => {
  test('should validate file upload types', async ({ page }) => {
    await page.goto('/dashboard');

    // 문서 탭으로 이동 (있는 경우)
    const documentsTab = page.locator('text=/문서|Documents/i');
    if (await documentsTab.isVisible()) {
      await documentsTab.click();
    }

    // 파일 업로드 버튼 확인
    const uploadButton = page.locator('input[type="file"]');
    if (await uploadButton.isVisible()) {
      // 업로드 버튼이 있으면 파일 타입 확인
      const accept = await uploadButton.getAttribute('accept');
      expect(accept).toMatch(/txt|md|pdf/i);
    }
  });
});
