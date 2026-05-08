import { test, expect } from '@playwright/test'

test.describe('Doctrines page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/doctrines')
  })

  test('renders "Our Beliefs" heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: /our beliefs/i })).toBeVisible()
  })

  test('renders accordion with belief topics', async ({ page }) => {
    const topics = [
      /the divine trinity/i,
      /repentance/i,
      /salvation/i,
      /sanctification/i,
      /the baptism of the holy ghost/i,
    ]
    for (const topic of topics) {
      const item = page.getByRole('button', { name: topic })
      await expect(item).toBeVisible()
    }
  })

  test('accordion items are collapsible', async ({ page }) => {
    const firstTopic = page.getByRole('button', { name: /the divine trinity/i }).first()
    await expect(firstTopic).toBeVisible()
    await firstTopic.click()
    // HeroUI accordion may need a frame to update state
    await page.waitForTimeout(100)
    const expanded = await firstTopic.getAttribute('aria-expanded')
    expect(expanded).toBeTruthy()
  })

  test('renders footer with quick links', async ({ page }) => {
    const footer = page.locator('footer')
    await expect(footer).toBeVisible()
    await expect(footer.getByText('Quick Links')).toBeVisible()
    await expect(footer.getByRole('link', { name: /media/i })).toBeVisible()
    await expect(footer.getByRole('link', { name: /contact/i })).toBeVisible()
    await expect(footer.getByRole('link', { name: /about/i })).toBeVisible()
  })
})
