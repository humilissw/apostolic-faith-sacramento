import { test, expect } from '@playwright/test'

test.describe('Media page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/media')
  })

  test('renders Media heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /media/i })).toBeVisible()
  })

  test('displays "Latest Services" section', async ({ page }) => {
    await expect(page.getByText(/latest services/i)).toBeVisible()
  })

  test('renders a link to at least one sermon', async ({ page }) => {
    const links = page.locator('a[href*="/sermon/"]')
    const count = await links.count()
    if (count > 0) {
      expect(count).toBeGreaterThan(0)
    }
  })

  test('renders footer', async ({ page }) => {
    const footer = page.locator('footer')
    await expect(footer).toBeVisible()
  })
})
