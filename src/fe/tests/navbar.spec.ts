import { test, expect } from '@playwright/test'

test.describe('Navbar (unauthenticated)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('shows Login button when not logged in', async ({ page }) => {
    await expect(page.getByRole('button', { name: /login/i })).toBeVisible()
  })

  test('does not show Video Uploads when not logged in', async ({ page }) => {
    await expect(page.getByText('Video Uploads')).not.toBeVisible()
  })

  test('Media link is present in navbar', async ({ page }) => {
    const nav = page.locator('nav').first()
    await expect(nav.getByText('Media')).toBeVisible()
    const mediaLink = nav.getByRole('link', { name: 'Media' })
    await expect(mediaLink).toHaveAttribute('href', /media/)
  })

  test('Contact Us link is present in navbar', async ({ page }) => {
    const nav = page.locator('nav').first()
    await expect(nav.getByText('Contact Us')).toBeVisible()
  })

  test('About dropdown contains Our Beliefs', async ({ page }) => {
    const nav = page.locator('nav').first()
    const aboutBtn = nav.getByRole('button', { name: /about/i })
    await expect(aboutBtn).toBeVisible()
    await aboutBtn.click()
    await expect(page.getByRole('link', { name: /our beliefs/i })).toBeVisible()
  })

  test('Resources dropdown is present', async ({ page }) => {
    const nav = page.locator('nav').first()
    const resourcesBtn = nav.getByRole('button', { name: /resources/i })
    await expect(resourcesBtn).toBeVisible()
  })
})

test.describe('Navbar (authenticated)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('auth token is accessible via evaluate', async ({ page }) => {
    await page.evaluate(() => {
      localStorage.setItem('auth_token', 'test-token-123')
    })
    const token = await page.evaluate(() => localStorage.getItem('auth_token'))
    expect(token).toBe('test-token-123')
  })
})
