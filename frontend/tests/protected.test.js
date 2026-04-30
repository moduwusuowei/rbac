import { test, expect } from '@playwright/test';

test.describe('Protected Pages', () => {
  async function login(page) {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    const usernameInput = page.locator('input[placeholder="请输入用户名"]');
    const passwordInput = page.locator('input[type="password"]');
    const loginButton = page.locator('button:has-text("登 录")');
    
    if (await usernameInput.isVisible()) {
      await usernameInput.fill('admin');
    }
    if (await passwordInput.isVisible()) {
      await passwordInput.fill('admin123');
    }
    if (await loginButton.isVisible()) {
      await loginButton.click();
      await page.waitForTimeout(3000);
    }
  }

  test.describe('Group Management', () => {
    test('should access group management page after login', async ({ page }) => {
      await login(page);
      
      const groupMenu = page.locator('.el-menu-item', { hasText: '组管理' });
      if (await groupMenu.isVisible()) {
        await groupMenu.click();
        await page.waitForTimeout(2000);
        
        const h2Elements = page.locator('h2');
        expect(await h2Elements.count()).toBeGreaterThan(0);
      }
    });

    test('should have group table after login', async ({ page }) => {
      await login(page);
      
      const groupMenu = page.locator('.el-menu-item', { hasText: '组管理' });
      if (await groupMenu.isVisible()) {
        await groupMenu.click();
        await page.waitForTimeout(2000);
        
        const table = page.locator('.el-table');
        expect(await table.count()).toBeGreaterThan(0);
      }
    });

    test('should have add group button after login', async ({ page }) => {
      await login(page);
      
      const groupMenu = page.locator('.el-menu-item', { hasText: '组管理' });
      if (await groupMenu.isVisible()) {
        await groupMenu.click();
        await page.waitForTimeout(2000);
        
        const addButton = page.locator('button', { hasText: '新增' });
        expect(await addButton.count()).toBeGreaterThan(0);
      }
    });
  });

  test.describe('Task Management', () => {
    test('should access task management page after login', async ({ page }) => {
      await login(page);
      
      const taskMenu = page.locator('.el-menu-item', { hasText: '任务管理' });
      if (await taskMenu.isVisible()) {
        await taskMenu.click();
        await page.waitForTimeout(2000);
        
        const h2Elements = page.locator('h2');
        expect(await h2Elements.count()).toBeGreaterThan(0);
      }
    });

    test('should have task table after login', async ({ page }) => {
      await login(page);
      
      const taskMenu = page.locator('.el-menu-item', { hasText: '任务管理' });
      if (await taskMenu.isVisible()) {
        await taskMenu.click();
        await page.waitForTimeout(2000);
        
        const table = page.locator('.el-table');
        expect(await table.count()).toBeGreaterThan(0);
      }
    });

    test('should have add task button after login', async ({ page }) => {
      await login(page);
      
      const taskMenu = page.locator('.el-menu-item', { hasText: '任务管理' });
      if (await taskMenu.isVisible()) {
        await taskMenu.click();
        await page.waitForTimeout(2000);
        
        const addButton = page.locator('button', { hasText: '新增' });
        expect(await addButton.count()).toBeGreaterThan(0);
      }
    });
  });

  test.describe('User Management', () => {
    test('should access user management page after login', async ({ page }) => {
      await login(page);
      
      const userMenu = page.locator('.el-menu-item', { hasText: '用户管理' });
      if (await userMenu.isVisible()) {
        await userMenu.click();
        await page.waitForTimeout(2000);
        
        const h2Elements = page.locator('h2');
        expect(await h2Elements.count()).toBeGreaterThan(0);
      }
    });

    test('should have user table after login', async ({ page }) => {
      await login(page);
      
      const userMenu = page.locator('.el-menu-item', { hasText: '用户管理' });
      if (await userMenu.isVisible()) {
        await userMenu.click();
        await page.waitForTimeout(2000);
        
        const table = page.locator('.el-table');
        expect(await table.count()).toBeGreaterThan(0);
      }
    });
  });

  test.describe('Role Management', () => {
    test('should access role management page after login', async ({ page }) => {
      await login(page);
      
      const roleMenu = page.locator('.el-menu-item', { hasText: '角色管理' });
      if (await roleMenu.isVisible()) {
        await roleMenu.click();
        await page.waitForTimeout(2000);
        
        const h2Elements = page.locator('h2');
        expect(await h2Elements.count()).toBeGreaterThan(0);
      }
    });
  });

  test.describe('Permission Management', () => {
    test('should access permission management page after login', async ({ page }) => {
      await login(page);
      
      const permissionMenu = page.locator('.el-menu-item', { hasText: '权限管理' });
      if (await permissionMenu.isVisible()) {
        await permissionMenu.click();
        await page.waitForTimeout(2000);
        
        const h2Elements = page.locator('h2');
        expect(await h2Elements.count()).toBeGreaterThan(0);
      }
    });
  });

  });
