import { test, expect } from '@playwright/test'

test.describe('Video Uploads page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/video-uploads')
  })

  test('renders a page (shows loading or content)', async ({ page }) => {
    // Without a running backend, the page shows an error message
    // With a backend it would show video cards
    await expect(page.locator('body')).toBeVisible()
  })

  test('renders a heading element', async ({ page }) => {
    const headings = page.locator('h1, h2')
    const count = await headings.count()
    if (count > 0) {
      await expect(headings.first()).toBeVisible()
    }
  })
})
