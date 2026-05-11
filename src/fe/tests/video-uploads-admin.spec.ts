import { test, expect } from '@playwright/test'

test.describe('Video uploads admin page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="email"]', 'superuser@example.com')
    await page.fill('input[type="password"]', 'supersecretpassword')
    await page.click('button[type="submit"]')
    await page.waitForURL('/video-uploads-admin')
  })

  test('renders page heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Video Upload Management' })).toBeVisible()
  })

  test('renders New button', async ({ page }) => {
    await expect(page.getByRole('button', { name: /New/i })).toBeVisible()
  })
})
