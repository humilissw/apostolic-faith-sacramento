import { test, expect } from '@playwright/test'

test.describe('Login page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login')
  })

  test('renders login heading', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Login' })).toBeVisible()
  })

  test('renders username input', async ({ page }) => {
    const usernameInput = page.locator('#username')
    await expect(usernameInput).toBeVisible()
    await expect(usernameInput).toHaveAttribute('type', 'text')
  })

  test('renders password input', async ({ page }) => {
    const passwordInput = page.locator('#password')
    await expect(passwordInput).toBeVisible()
    await expect(passwordInput).toHaveAttribute('type', 'password')
  })

  test('renders login button', async ({ page }) => {
    const loginBtn = page.getByRole('button', { name: 'Login' })
    await expect(loginBtn).toBeVisible()
  })

  test('renders forgot password link', async ({ page }) => {
    const forgotLink = page.getByRole('link', { name: 'Forgot password?' })
    await expect(forgotLink).toBeVisible()
    await expect(forgotLink).toHaveAttribute('href', '/forgot-password/')
  })

  test('renders show/hide password toggle', async ({ page }) => {
    const toggle = page.getByRole('button', { name: /show/i })
    await expect(toggle).toBeVisible()
  })

  test('navigates back to home via logo', async ({ page }) => {
    const logo = page.getByAltText(/apostolic faith church/i)
    await logo.click()
    await expect(page).toHaveURL('/')
  })
})
