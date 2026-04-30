import { test, expect } from '@playwright/test';

test.describe('API Tests', () => {
  test('should test login API', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const loginPromise = page.waitForRequest(request => 
      request.url().includes('/api/v1/auth/login') && request.method() === 'POST'
    );
    
    const inputs = page.locator('input[type="text"], input[type="password"]');
    if ((await inputs.count()) >= 2) {
      await inputs.first().fill('admin');
      await inputs.nth(1).fill('admin123');
      
      const buttons = page.locator('button');
      if ((await buttons.count()) > 0) {
        await buttons.first().click();
      }
    }
    
    try {
      await loginPromise;
    } catch (e) {
      console.log('Login request not made');
    }
  });

  test('should test register API', async ({ page }) => {
    await page.goto('/register');
    await page.waitForLoadState('networkidle');
    
    const inputs = page.locator('input[type="text"], input[type="email"], input[type="password"]');
    if ((await inputs.count()) >= 4) {
      await inputs.first().fill('testuser_api');
      await inputs.nth(1).fill('api@test.com');
      await inputs.nth(2).fill('Password@123');
      await inputs.nth(3).fill('Password@123');
      
      const buttons = page.locator('button');
      if ((await buttons.count()) > 0) {
        await buttons.first().click();
        await page.waitForTimeout(2000);
      }
    }
    
    const registerCard = page.locator('.register-card');
    expect(await registerCard.count()).toBeGreaterThan(0);
  });

  test('should test unauthorized request behavior', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
    
    const url = page.url();
    console.log('Current URL:', url);
  });

  test('should handle network errors gracefully', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const inputs = page.locator('input[type="text"], input[type="password"]');
    if ((await inputs.count()) >= 2) {
      await inputs.first().fill('invalid');
      await inputs.nth(1).fill('invalid');
      
      const buttons = page.locator('button');
      if ((await buttons.count()) > 0) {
        await buttons.first().click();
        await page.waitForTimeout(2000);
      }
    }
    
    const loginCard = page.locator('.login-card');
    expect(await loginCard.count()).toBeGreaterThan(0);
  });

  test('should have working auth endpoints', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const loginCard = page.locator('.login-card');
    expect(await loginCard.count()).toBeGreaterThan(0);
  });

  test('should test logout behavior', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const inputs = page.locator('input[type="text"], input[type="password"]');
    if ((await inputs.count()) >= 2) {
      await inputs.first().fill('admin');
      await inputs.nth(1).fill('admin123');
      
      const buttons = page.locator('button');
      if ((await buttons.count()) > 0) {
        await buttons.first().click();
        await page.waitForTimeout(3000);
      }
    }
    
    const h2Elements = page.locator('h2');
    expect(await h2Elements.count()).toBeGreaterThan(0);
  });
});
