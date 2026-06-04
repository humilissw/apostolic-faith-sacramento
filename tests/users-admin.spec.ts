import { test, expect } from '@playwright/test'

test.describe('Users admin page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', 'superuser@example.com')
    await page.fill('input[type="password"]', 'supersecretpassword')
    await page.click('button[type="submit"]')
    await page.waitForURL('/users-admin')
  })

  test('renders page heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'User Management' })).toBeVisible()
  })

  test('renders table header', async ({ page }) => {
    const headers = page.locator('thead th')
    await expect(headers).toHaveCount(5)
  })
})
