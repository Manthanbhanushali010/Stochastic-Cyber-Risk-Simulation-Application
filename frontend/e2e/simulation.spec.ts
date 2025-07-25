import { test, expect } from '@playwright/test';

/**
 * End-to-End Simulation Tests
 * Tests the complete Monte Carlo simulation workflow
 */
test.describe('🎯 Simulation Workflow', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/login');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should navigate to simulation page', async ({ page }) => {
    await page.click('text=New Simulation');
    await expect(page).toHaveURL('/simulation');
    await expect(page.locator('h1')).toContainText('Monte Carlo Simulation');
  });

  test('should display simulation form with all required fields', async ({ page }) => {
    await page.goto('/simulation');
    
    // Check form sections
    await expect(page.locator('[data-testid="simulation-name"]')).toBeVisible();
    await expect(page.locator('[data-testid="simulation-description"]')).toBeVisible();
    await expect(page.locator('[data-testid="iterations"]')).toBeVisible();
    await expect(page.locator('[data-testid="frequency-distribution"]')).toBeVisible();
    await expect(page.locator('[data-testid="severity-distribution"]')).toBeVisible();
    await expect(page.locator('[data-testid="portfolio-value"]')).toBeVisible();
  });

  test('should validate required fields', async ({ page }) => {
    await page.goto('/simulation');
    
    // Try to submit empty form
    await page.click('button[type="submit"]');
    
    // Check validation errors
    await expect(page.locator('.error-text')).toContainText('Simulation name is required');
    await expect(page.locator('.error-text')).toContainText('Number of iterations is required');
  });

  test('should create and run simulation successfully', async ({ page }) => {
    await page.goto('/simulation');
    
    // Fill simulation form
    await page.fill('[data-testid="simulation-name"]', 'Test Simulation');
    await page.fill('[data-testid="simulation-description"]', 'E2E test simulation');
    await page.fill('[data-testid="iterations"]', '1000');
    
    // Select frequency distribution
    await page.selectOption('[data-testid="frequency-distribution"]', 'poisson');
    await page.fill('[data-testid="frequency-lambda"]', '2.5');
    
    // Select severity distribution
    await page.selectOption('[data-testid="severity-distribution"]', 'lognormal');
    await page.fill('[data-testid="severity-mean"]', '10');
    await page.fill('[data-testid="severity-std"]', '1.5');
    
    // Portfolio settings
    await page.fill('[data-testid="portfolio-value"]', '1000000');
    await page.fill('[data-testid="policy-limit"]', '500000');
    await page.fill('[data-testid="deductible"]', '10000');
    
    // Submit simulation
    await page.click('button[type="submit"]');
    
    // Wait for progress indicator
    await expect(page.locator('.progress-bar')).toBeVisible();
    await expect(page.locator('.progress-message')).toContainText('Initializing simulation');
    
    // Wait for completion and redirect to results
    await page.waitForURL('/results/*', { timeout: 60000 });
    await expect(page.locator('h1')).toContainText('Simulation Results');
  });

  test('should apply preset scenarios', async ({ page }) => {
    await page.goto('/simulation');
    
    // Select a preset scenario
    await page.selectOption('[data-testid="preset-scenarios"]', 'advanced-persistent-threat');
    
    // Verify preset values are applied
    await expect(page.locator('[data-testid="simulation-name"]')).toHaveValue('Advanced Persistent Threat');
    await expect(page.locator('[data-testid="frequency-distribution"]')).toHaveValue('poisson');
    await expect(page.locator('[data-testid="severity-distribution"]')).toHaveValue('lognormal');
  });

  test('should clone existing simulation', async ({ page }) => {
    // First create a simulation
    await page.goto('/simulation');
    await page.fill('[data-testid="simulation-name"]', 'Original Simulation');
    await page.fill('[data-testid="iterations"]', '1000');
    await page.fill('[data-testid="portfolio-value"]', '1000000');
    
    // Navigate to simulation list
    await page.goto('/dashboard');
    await expect(page.locator('.simulation-card')).toContainText('Original Simulation');
    
    // Clone simulation
    await page.click('.simulation-card .clone-button');
    await expect(page).toHaveURL('/simulation?clone=*');
    
    // Verify cloned values
    await expect(page.locator('[data-testid="simulation-name"]')).toHaveValue('Original Simulation (Copy)');
    await expect(page.locator('[data-testid="iterations"]')).toHaveValue('1000');
  });

  test('should show real-time progress updates', async ({ page }) => {
    await page.goto('/simulation');
    
    // Fill minimum required fields
    await page.fill('[data-testid="simulation-name"]', 'Progress Test');
    await page.fill('[data-testid="iterations"]', '5000');
    await page.fill('[data-testid="portfolio-value"]', '1000000');
    
    // Submit simulation
    await page.click('button[type="submit"]');
    
    // Monitor progress updates
    const progressBar = page.locator('.progress-bar');
    const progressMessage = page.locator('.progress-message');
    
    await expect(progressBar).toBeVisible();
    await expect(progressMessage).toContainText('Initializing');
    
    // Wait for progress changes
    await expect(progressMessage).toContainText('Running Monte Carlo', { timeout: 10000 });
    
    // Check that progress value increases
    const initialProgress = await progressBar.getAttribute('value');
    await page.waitForTimeout(2000);
    const laterProgress = await progressBar.getAttribute('value');
    
    expect(parseFloat(laterProgress || '0')).toBeGreaterThan(parseFloat(initialProgress || '0'));
  });

  test('should handle simulation errors gracefully', async ({ page }) => {
    await page.goto('/simulation');
    
    // Fill form with invalid values that might cause server errors
    await page.fill('[data-testid="simulation-name"]', 'Error Test');
    await page.fill('[data-testid="iterations"]', '999999999'); // Extremely large number
    await page.fill('[data-testid="portfolio-value"]', '0'); // Invalid portfolio value
    
    await page.click('button[type="submit"]');
    
    // Wait for error message
    await expect(page.locator('.error-notification')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('.error-notification')).toContainText(/Error|Failed/);
  });

  test('should validate distribution parameters', async ({ page }) => {
    await page.goto('/simulation');
    
    // Select Poisson distribution
    await page.selectOption('[data-testid="frequency-distribution"]', 'poisson');
    
    // Enter invalid lambda (negative value)
    await page.fill('[data-testid="frequency-lambda"]', '-1');
    
    await page.click('button[type="submit"]');
    
    // Check validation error
    await expect(page.locator('.error-text')).toContainText('Lambda must be positive');
  });

  test('should show confidence levels in results', async ({ page }) => {
    // Run a quick simulation
    await page.goto('/simulation');
    await page.fill('[data-testid="simulation-name"]', 'Confidence Test');
    await page.fill('[data-testid="iterations"]', '1000');
    await page.fill('[data-testid="portfolio-value"]', '1000000');
    
    // Set confidence levels
    await page.fill('[data-testid="confidence-levels"]', '90,95,99');
    
    await page.click('button[type="submit"]');
    
    // Wait for results
    await page.waitForURL('/results/*', { timeout: 60000 });
    
    // Check that all confidence levels are displayed
    await expect(page.locator('[data-testid="var-90"]')).toBeVisible();
    await expect(page.locator('[data-testid="var-95"]')).toBeVisible();
    await expect(page.locator('[data-testid="var-99"]')).toBeVisible();
  });
}); 