# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: doctrines.spec.ts >> Doctrines page >> renders "Our Beliefs" heading
- Location: tests/doctrines.spec.ts:8:2

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByRole('heading', { name: /our beliefs/i })
Expected: visible
Error: element(s) not found

Call log:
  - Expect "to.be.visible" with timeout 10000ms
  - waiting for getByRole('heading', { name: /our beliefs/i })

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test'
  2  |
  3  | test.describe('Doctrines page', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('/doctrines')
  6  |   })
  7  |
  8  |   test('renders "Our Beliefs" heading', async ({ page }) => {
> 9  |     await expect(page.getByRole('heading', { name: /our beliefs/i })).toBeVisible()
     |                                                                      ^ Error: expect(locator).toBeVisible() failed
  10 |   })
  11 |
  12 |   test('renders accordion with belief topics', async ({ page }) => {
  13 |     const topics = [
  14 |       /the divine trinity/i,
  15 |       /repentance/i,
  16 |       /salvation/i,
  17 |       /sanctification/i,
  18 |       /the baptism of the holy ghost/i,
  19 |     ]
  20 |     for (const topic of topics) {
  21 |       const item = page.getByRole('button', { name: topic })
  22 |       await expect(item).toBeVisible()
  23 |     }
  24 |   })
  25 |
  26 |   test('accordion items are collapsible', async ({ page }) => {
  27 |     const firstTopic = page.getByRole('button', { name: /the divine trinity/i }).first()
  28 |     await expect(firstTopic).toBeVisible()
  29 |     await firstTopic.click()
  30 |     // HeroUI accordion may need a frame to update state
  31 |     await page.waitForTimeout(100)
  32 |     const expanded = await firstTopic.getAttribute('aria-expanded')
  33 |     expect(expanded).toBeTruthy()
  34 |   })
  35 |
  36 |   test('renders footer with quick links', async ({ page }) => {
  37 |     const footer = page.locator('footer')
  38 |     await expect(footer).toBeVisible()
  39 |     await expect(footer.getByText('Quick Links')).toBeVisible()
  40 |     await expect(footer.getByRole('link', { name: /media/i })).toBeVisible()
  41 |     await expect(footer.getByRole('link', { name: /contact/i })).toBeVisible()
  42 |     await expect(footer.getByRole('link', { name: /about/i })).toBeVisible()
  43 |   })
  44 | })
  45 |
```
