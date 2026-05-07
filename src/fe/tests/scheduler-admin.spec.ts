import { test, expect } from '@playwright/test'

test.describe('Scheduler admin page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('#username', 'superuser@example.com')
    await page.fill('input[type="password"]', 'supersecretpassword')
    await page.click('button[type="submit"]')
    await page.waitForURL('/scheduler-admin')
  })

  test('renders page heading', async ({ page }) => {
    await expect(page.getByText(/Scheduler Admin/i)).toBeVisible()
  })
})
