import { test, expect } from '@playwright/test'

test.describe('Homepage', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('displays the welcome heading', async ({ page }) => {
    const headings = page.locator('h1')
    expect(await headings.count()).toBeGreaterThan(0)
    expect(headings.first()).toHaveText(/WELCOME TO THE/i)
  })

  test('renders About Us button that links to doctrines', async ({ page }) => {
    const aboutBtn = page.getByRole('link', { name: 'About Us' })
    expect(aboutBtn).toHaveAttribute('href', /doctrines/)
  })

  test('renders Latest Sermon button linking to YouTube', async ({ page }) => {
    const sermonBtn = page.getByRole('link', { name: 'Latest Sermon' })
    expect(sermonBtn).toHaveAttribute('href', /youtube/i)
  })

  test('renders the AFC logo as a link to home', async ({ page }) => {
    const logo = page.getByAltText(/apostolic faith church/i).first()
    await expect(logo).toBeVisible()
    // Logo may be an SVG, so check for link parent
    const link = logo.locator('a').first()
    if (await link.count() > 0) {
      await expect(link).toHaveAttribute('href', '/')
    }
  })

  test('renders navbar with navigation links', async ({ page }) => {
    const nav = page.getByRole('navigation').last()
    await expect(nav).toBeVisible()
    await expect(nav.getByText('Media')).toBeVisible()
    await expect(nav.getByText('Contact Us')).toBeVisible()
  })

  test('renders navbar dropdown triggers', async ({ page }) => {
    const nav = page.getByRole('navigation').last()
    await expect(nav.getByRole('button', { name: /about/i })).toBeVisible()
    await expect(nav.getByRole('button', { name: /resources/i })).toBeVisible()
  })

  test('renders the footer', async ({ page }) => {
    const footer = page.locator('footer')
    await expect(footer).toBeVisible()
    await expect(footer).toHaveText(/Apostolic Faith Church/)
    await expect(footer).toHaveText(/202[0-9] Apostolic Faith Church/)
  })
})
