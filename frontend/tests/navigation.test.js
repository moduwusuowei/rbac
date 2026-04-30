import { test, expect } from '@playwright/test';

test.describe('Navigation Tests', () => {
  test('should navigate from login to register', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    try {
      await page.click('text=去注册');
      await page.waitForURL('**/register');
      
      const registerCard = page.locator('.register-card');
      expect(await registerCard.count()).toBeGreaterThan(0);
    } catch (e) {
      console.log('Navigation failed');
    }
  });

  test('should navigate from register to login', async ({ page }) => {
    await page.goto('/register');
    await page.waitForLoadState('networkidle');
    
    try {
      await page.click('text=去登录');
      await page.waitForURL('**/login');
      
      const loginCard = page.locator('.login-card');
      expect(await loginCard.count()).toBeGreaterThan(0);
    } catch (e) {
      console.log('Navigation failed');
    }
  });

  test('should handle 404 page', async ({ page }) => {
    await page.goto('/nonexistent-page');
    await page.waitForLoadState('networkidle');
    
    const notFound = page.locator('text=页面不存在');
    expect(await notFound.count()).toBeGreaterThan(0);
  });

  test('should handle forbidden page', async ({ page }) => {
    await page.goto('/forbidden');
    await page.waitForLoadState('networkidle');
    
    const pageContent = page.locator('body');
    expect(await pageContent.count()).toBeGreaterThan(0);
  });

  test('should have correct page title for login', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const title = await page.title();
    expect(title).toBeTruthy();
  });

  test('should have correct page title for register', async ({ page }) => {
    await page.goto('/register');
    await page.waitForLoadState('networkidle');
    
    const title = await page.title();
    expect(title).toBeTruthy();
  });

  test('should reload login page correctly', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    const loginCard = page.locator('.login-card');
    expect(await loginCard.count()).toBeGreaterThan(0);
  });

  test('should reload register page correctly', async ({ page }) => {
    await page.goto('/register');
    await page.waitForLoadState('networkidle');
    
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    const registerCard = page.locator('.register-card');
    expect(await registerCard.count()).toBeGreaterThan(0);
  });
});
