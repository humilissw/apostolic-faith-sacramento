import { defineConfig, devices } from '@playwright/test'

const baseURL = 'https://localhost:3000'

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  expect: {
    timeout: 10_000,
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    headless: true,
    baseURL,
    // The dev stack serves HTTPS with self-signed / mkcert certs that may not
    // be trusted by the test browser — bypass cert validation (dev only) so
    // navigations don't fail with net::ERR_CERT_AUTHORITY_INVALID.
    ignoreHTTPSErrors: true,
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  webServer: {
    command: 'bun run dev',
    port: 3000,
    timeout: 60_000,
    stdout: 'pipe',
    reuseExistingServer: true,
  },
})
