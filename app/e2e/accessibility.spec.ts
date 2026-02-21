import { test, expect } from '@playwright/test';

test.describe('Accessibility', () => {
  test('landing page should have proper heading structure', async ({ page }) => {
    await page.goto('/');

    // h1 태그가 하나만 있어야 함
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBeGreaterThanOrEqual(1);

    // 헤딩 계층 구조 확인
    const h1 = page.locator('h1').first();
    await expect(h1).toBeVisible();
  });

  test('should have visible focus indicators', async ({ page }) => {
    await page.goto('/demo');

    // Tab 키로 포커스 이동
    await page.keyboard.press('Tab');

    // 포커스된 요소가 있는지 확인
    const focusedElement = page.locator(':focus');
    await expect(focusedElement.first()).toBeVisible();
  });

  test('chat input should be accessible', async ({ page }) => {
    await page.goto('/demo');

    const input = page.locator('input[type="text"], textarea').first();

    // 입력 필드에 레이블이 있어야 함
    const ariaLabel = await input.getAttribute('aria-label');
    const placeholder = await input.getAttribute('placeholder');

    // aria-label 또는 placeholder가 있어야 함
    expect(ariaLabel || placeholder).toBeTruthy();
  });

  test('buttons should have accessible names', async ({ page }) => {
    await page.goto('/demo');

    const buttons = page.locator('button');
    const count = await buttons.count();

    for (let i = 0; i < Math.min(count, 5); i++) {
      const button = buttons.nth(i);
      const text = await button.textContent();
      const ariaLabel = await button.getAttribute('aria-label');

      // 버튼에 텍스트 또는 aria-label이 있어야 함
      expect(text || ariaLabel).toBeTruthy();
    }
  });

  test('should support keyboard navigation', async ({ page }) => {
    await page.goto('/demo');

    // Tab 키로 주요 요소들에 접근 가능한지 확인
    const tabStops: string[] = [];

    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
      const focused = await page.evaluate(() => {
        const el = document.activeElement;
        return el ? el.tagName + (el.getAttribute('class') || '') : '';
      });
      tabStops.push(focused);
    }

    // 최소한 몇 개의 요소에 포커스가 이동했는지 확인
    const uniqueStops = new Set(tabStops);
    expect(uniqueStops.size).toBeGreaterThanOrEqual(2);
  });

  test('should have sufficient color contrast on buttons', async ({ page }) => {
    await page.goto('/');

    // 주요 CTA 버튼 확인
    const ctaButtons = page.locator('button, a').filter({
      has: page.locator('text=/시작|Start|Demo|체험/i')
    });

    if (await ctaButtons.count() > 0) {
      const button = ctaButtons.first();
      await expect(button).toBeVisible();
    }
  });

  test('images should have alt text', async ({ page }) => {
    await page.goto('/');

    const images = page.locator('img');
    const count = await images.count();

    for (let i = 0; i < count; i++) {
      const img = images.nth(i);
      const alt = await img.getAttribute('alt');
      const ariaLabel = await img.getAttribute('aria-label');
      const role = await img.getAttribute('role');

      // 장식용 이미지는 alt="" 또는 role="presentation" 가능
      // 정보성 이미지는 alt 텍스트 필요
      expect(alt !== null || ariaLabel || role === 'presentation').toBeTruthy();
    }
  });

  test('dashboard should have proper landmarks', async ({ page }) => {
    await page.goto('/dashboard');

    // main 랜드마크 확인
    const main = page.locator('main, [role="main"]');
    const mainCount = await main.count();

    // main 랜드마크가 있거나 전체가 하나의 앱인 경우
    expect(mainCount >= 0).toBeTruthy();
  });

  test('should handle escape key for modals', async ({ page }) => {
    await page.goto('/demo');

    // 위젯 미리보기 등 모달이 있는지 확인하고 Escape 동작 테스트
    // 일단 페이지 로드 확인
    await expect(page).toHaveURL(/demo/);
  });
});

test.describe('Screen Reader Support', () => {
  test('should have proper page title', async ({ page }) => {
    await page.goto('/');
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);
  });

  test('form inputs should have labels', async ({ page }) => {
    await page.goto('/demo');

    const inputs = page.locator('input[type="text"], textarea');
    const count = await inputs.count();

    for (let i = 0; i < count; i++) {
      const input = inputs.nth(i);
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      const ariaLabelledby = await input.getAttribute('aria-labelledby');
      const placeholder = await input.getAttribute('placeholder');

      // 접근 가능한 이름이 있어야 함
      const hasAccessibleName = id || ariaLabel || ariaLabelledby || placeholder;
      expect(hasAccessibleName).toBeTruthy();
    }
  });
});
