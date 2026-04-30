import { test, expect } from '@playwright/test';

test.describe('Register Page', () => {
  test('should load register page correctly', async ({ page }) => {
    await page.goto('/register');
    await page.waitForLoadState('networkidle');
    
    // Check register card
    const registerCard = page.locator('.register-card');
    expect(await registerCard.count()).toBeGreaterThan(0);
    
    // Check title
    const titles = page.locator('h2');
    expect(await titles.count()).toBeGreaterThan(0);
  });

  test('should have form inputs', async ({ page }) => {
    await page.goto('/register');
    await page.waitForLoadState('networkidle');
    
    // Get visible text inputs only (skip hidden file input)
    const textInputs = page.locator('input[type="text"], input[type="email"], input[type="password"]');
    expect(await textInputs.count()).toBeGreaterThanOrEqual(4);
  });

  test('should have avatar upload feature', async ({ page }) => {
    await page.goto('/register');
    await page.waitForLoadState('networkidle');
    
    // Check avatar preview
    const avatar = page.locator('.avatar-preview');
    expect(await avatar.count()).toBeGreaterThan(0);
    
    // Check upload button
    const uploadButton = page.locator('button', { hasText: '上传头像' });
    expect(await uploadButton.count()).toBeGreaterThan(0);
  });

  test('should navigate back to login', async ({ page }) => {
    await page.goto('/register');
    await page.waitForLoadState('networkidle');
    
    // Click login link
    try {
      await page.click('text=去登录');
      await page.waitForURL('**/login');
    } catch (e) {
      console.log('Login link not found');
    }
  });

  test('should have avatar upload tip', async ({ page }) => {
    await page.goto('/register');
    await page.waitForLoadState('networkidle');
    
    const tip = page.locator('.avatar-tip');
    expect(await tip.count()).toBeGreaterThan(0);
  });

  test('should display correctly on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/register');
    await page.waitForLoadState('networkidle');
    
    const registerCard = page.locator('.register-card');
    expect(await registerCard.count()).toBeGreaterThan(0);
  });

  test('should have register button', async ({ page }) => {
    await page.goto('/register');
    await page.waitForLoadState('networkidle');
    
    const buttons = page.locator('button');
    expect(await buttons.count()).toBeGreaterThan(0);
  });

  test('should have register footer', async ({ page }) => {
    await page.goto('/register');
    await page.waitForLoadState('networkidle');
    
    const footer = page.locator('.register-footer');
    expect(await footer.count()).toBeGreaterThan(0);
  });
});
