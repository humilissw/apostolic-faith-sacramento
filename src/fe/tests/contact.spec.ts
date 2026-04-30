import { test, expect } from '@playwright/test'

test.describe('Contact page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/contact')
  })

  test('renders Contact heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Contact', exact: true }).first()).toBeVisible()
  })

  test('renders Google Maps iframe', async ({ page }) => {
    const iframe = page.locator('iframe').first()
    await expect(iframe).toBeVisible()
  })

  test('renders church address', async ({ page }) => {
    await expect(page.getByRole('main').getByText(/Elmont Ave/i).first()).toBeVisible()
  })

  test('renders mailing address', async ({ page }) => {
    await expect(page.getByRole('main').getByText(/Wortell Drive/i).first()).toBeVisible()
  })

  test('renders email links', async ({ page }) => {
    await expect(page.getByRole('link', { name: 'info@afcsacramento.org' }).first()).toBeVisible()
    await expect(page.getByRole('link', { name: 'pete@sferle.com' }).first()).toBeVisible()
  })

  test('renders footer', async ({ page }) => {
    const footer = page.locator('footer')
    await expect(footer).toBeVisible()
  })
})
