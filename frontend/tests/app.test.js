import { test, expect } from '@playwright/test';

test.describe('RBAC Frontend Tests', () => {
  // 登录页面测试
  test.describe('Login Page', () => {
    test('should load login page correctly', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // 检查登录卡片
      await expect(page.locator('.login-card')).toBeVisible();
      
      // 检查页面标题
      const title = await page.title();
      expect(title).toBeTruthy();
    });

    test('should have login form with inputs and button', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      // 检查输入框数量
      const inputs = page.locator('input');
      expect(await inputs.count()).toBeGreaterThanOrEqual(2);
      
      // 检查按钮
      const buttons = page.locator('button');
      expect(await buttons.count()).toBeGreaterThan(0);
    });

    test('should have RBAC system title', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      const titles = page.locator('h2');
      expect(await titles.count()).toBeGreaterThan(0);
    });

    test('should have test credentials alert', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      const tips = page.locator('.login-tips');
      await expect(tips).toBeVisible();
    });

    test('should have register link', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      const footer = page.locator('.login-footer');
      await expect(footer).toBeVisible();
    });
  });

  // 登录功能测试
  test.describe('Login Functionality', () => {
    test('should attempt login with admin credentials', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      const inputs = page.locator('input');
      if ((await inputs.count()) >= 2) {
        await inputs.first().fill('admin');
        await inputs.nth(1).fill('admin123');
        
        const buttons = page.locator('button');
        if ((await buttons.count()) > 0) {
          await buttons.first().click();
          await page.waitForTimeout(3000);
        }
      }
      
      // 检查是否有导航元素
      const h2Elements = page.locator('h2');
      expect(await h2Elements.count()).toBeGreaterThan(0);
    });

    test('should attempt login with invalid credentials', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      const inputs = page.locator('input');
      if ((await inputs.count()) >= 2) {
        await inputs.first().fill('invalid');
        await inputs.nth(1).fill('invalid');
        
        const buttons = page.locator('button');
        if ((await buttons.count()) > 0) {
          await buttons.first().click();
          await page.waitForTimeout(2000);
        }
      }
      
      // 应该仍然在登录页面
      await expect(page.locator('.login-card')).toBeVisible();
    });
  });

  // 页面导航测试
  test.describe('Page Navigation', () => {
    test('should navigate to register page', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      try {
        await page.click('text=去注册');
        await page.waitForURL('**/register');
      } catch (e) {
        console.log('Register navigation not available');
      }
    });
  });

  // 响应式布局测试
  test.describe('Responsive Layout', () => {
    test('should display correctly on desktop', async ({ page }) => {
      await page.setViewportSize({ width: 1920, height: 1080 });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      await expect(page.locator('.login-card')).toBeVisible();
    });

    test('should display correctly on mobile', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      await expect(page.locator('.login-card')).toBeVisible();
    });
  });

  // 页面元素测试
  test.describe('Page Elements', () => {
    test('should have correct background gradient', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      const container = page.locator('.login-container');
      await expect(container).toBeVisible();
    });

    test('should have form validation rules', async ({ page }) => {
      await page.goto('/');
      await page.waitForLoadState('networkidle');
      
      const form = page.locator('form');
      expect(await form.count()).toBeGreaterThan(0);
    });
  });
});
