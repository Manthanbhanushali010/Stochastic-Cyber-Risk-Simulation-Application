import { test, expect } from '@playwright/test';

/**
 * End-to-End Authentication Tests
 * Tests the complete user authentication flow
 */
test.describe('🔐 Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display login page', async ({ page }) => {
    await expect(page).toHaveTitle(/Stochastic Cyber Risk Simulation/);
    await expect(page.locator('h1')).toContainText('Welcome');
  });

  test('should register new user successfully', async ({ page }) => {
    // Navigate to registration
    await page.click('text=Register');
    await expect(page).toHaveURL('/register');
    
    // Fill registration form
    const timestamp = Date.now();
    const testUser = {
      email: `test-${timestamp}@example.com`,
      username: `testuser${timestamp}`,
      password: 'TestPassword123!',
      firstName: 'Test',
      lastName: 'User'
    };
    
    await page.fill('[name="email"]', testUser.email);
    await page.fill('[name="username"]', testUser.username);
    await page.fill('[name="password"]', testUser.password);
    await page.fill('[name="first_name"]', testUser.firstName);
    await page.fill('[name="last_name"]', testUser.lastName);
    
    // Submit registration
    await page.click('button[type="submit"]');
    
    // Verify successful registration
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('.welcome-message')).toContainText(`Welcome, ${testUser.firstName}`);
  });

  test('should login existing user successfully', async ({ page }) => {
    // Navigate to login
    await page.click('text=Login');
    await expect(page).toHaveURL('/login');
    
    // Fill login form with test credentials
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    
    // Submit login
    await page.click('button[type="submit"]');
    
    // Verify successful login
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('.user-menu')).toBeVisible();
  });

  test('should show validation errors for invalid login', async ({ page }) => {
    await page.click('text=Login');
    
    // Submit empty form
    await page.click('button[type="submit"]');
    
    // Check for validation errors
    await expect(page.locator('.error-message')).toContainText('Email is required');
    await expect(page.locator('.error-message')).toContainText('Password is required');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.click('text=Login');
    
    // Fill with invalid credentials
    await page.fill('[name="email"]', 'invalid@example.com');
    await page.fill('[name="password"]', 'wrongpassword');
    
    await page.click('button[type="submit"]');
    
    // Check for error message
    await expect(page.locator('.error-message')).toContainText('Invalid credentials');
  });

  test('should logout user successfully', async ({ page }) => {
    // Login first
    await page.click('text=Login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // Logout
    await page.click('.user-menu');
    await page.click('text=Logout');
    
    // Verify logout
    await expect(page).toHaveURL('/');
    await expect(page.locator('text=Login')).toBeVisible();
  });

  test('should redirect to login when accessing protected route', async ({ page }) => {
    // Try to access protected route directly
    await page.goto('/dashboard');
    
    // Should redirect to login
    await expect(page).toHaveURL('/login');
    await expect(page.locator('h1')).toContainText('Login');
  });

  test('should persist authentication across page refreshes', async ({ page }) => {
    // Login
    await page.click('text=Login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL('/dashboard');
    
    // Refresh page
    await page.reload();
    
    // Should still be authenticated
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('.user-menu')).toBeVisible();
  });
}); 