# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: contact.spec.ts >> Contact page >> renders Google Maps iframe
- Location: tests/contact.spec.ts:12:2

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: locator('iframe').first()
Expected: visible
Error: element(s) not found

Call log:
  - Expect "to.be.visible" with timeout 10000ms
  - waiting for locator('iframe').first()

```

# Test source

```ts
  1  | import { test, expect } from '@playwright/test'
  2  |
  3  | test.describe('Contact page', () => {
  4  |   test.beforeEach(async ({ page }) => {
  5  |     await page.goto('/contact')
  6  |   })
  7  |
  8  |   test('renders Contact heading', async ({ page }) => {
  9  |     await expect(page.getByRole('heading', { name: 'Contact', exact: true }).first()).toBeVisible()
  10 |   })
  11 |
  12 |   test('renders Google Maps iframe', async ({ page }) => {
  13 |     const iframe = page.locator('iframe').first()
> 14 |     await expect(iframe).toBeVisible()
     |                         ^ Error: expect(locator).toBeVisible() failed
  15 |   })
  16 |
  17 |   test('renders church address', async ({ page }) => {
  18 |     await expect(page.getByRole('main').getByText(/Elmont Ave/i).first()).toBeVisible()
  19 |   })
  20 |
  21 |   test('renders mailing address', async ({ page }) => {
  22 |     await expect(page.getByRole('main').getByText(/Wortell Drive/i).first()).toBeVisible()
  23 |   })
  24 |
  25 |   test('renders email links', async ({ page }) => {
  26 |     await expect(page.getByRole('link', { name: 'info@afcsacramento.org' }).first()).toBeVisible()
  27 |     await expect(page.getByRole('link', { name: 'pete@sferle.com' }).first()).toBeVisible()
  28 |   })
  29 |
  30 |   test('renders footer', async ({ page }) => {
  31 |     const footer = page.locator('footer')
  32 |     await expect(footer).toBeVisible()
  33 |   })
  34 | })
  35 |
```
