import { test, expect } from '@playwright/test'

test.describe('Live service page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/live-service')
  })

  test('renders Google Maps iframe', async ({ page }) => {
    const iframe = page.getByTitle('Apostolic Faith Church Location')
    await expect(iframe).toBeVisible()
  })

  test('renders church address', async ({ page }) => {
    await expect(page.getByText(/Elmont Ave/i)).toBeVisible()
  })

  test('renders mailing address', async ({ page }) => {
    await expect(page.getByText(/Wortell Drive/i)).toBeVisible()
  })

  test('email links are clickable', async ({ page }) => {
    const mailtoLinks = page.locator('a[href^="mailto:"]')
    await expect(mailtoLinks).toHaveCount(2)
    await expect(mailtoLinks.first()).toHaveAttribute('href', 'mailto:pete@sferle.com')
    await expect(mailtoLinks.last()).toHaveAttribute('href', 'mailto:info@afcsacramento.org')
  })
})
