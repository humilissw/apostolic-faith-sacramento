import { test, expect } from '@playwright/test'

test.describe('Integrations page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', 'superuser@example.com')
    await page.fill('input[type="password"]', 'supersecretpassword')
    await page.click('button[type="submit"]')
    await page.waitForURL('/integrations')
  })

  test('renders page heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Integrations' })).toBeVisible()
  })

  test('renders Pre-seed button', async ({ page }) => {
    await expect(page.getByRole('button', { name: /Pre-seed/i })).toBeVisible()
  })

  test('renders New Integration button', async ({ page }) => {
    await expect(page.getByRole('button', { name: /New Integration/i })).toBeVisible()
  })

  test('table header has correct columns', async ({ page }) => {
    const headers = page.locator('thead th')
    await expect(headers).toHaveCount(6)
  })
})
