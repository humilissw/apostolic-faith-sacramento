/** @jest-environment jsdom */

import { login } from '@/lib/api'

describe('API utilities', () => {
  beforeEach(() => {
    jest.restoreAllMocks()
  })

  describe('login (BFF-first)', () => {
    it('sends a JSON POST to the BFF /auth/login endpoint', async () => {
      const mockFetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ ok: true, code: 'one-time-code' }),
        }),
      )
      global.fetch = mockFetch

      await login('user@example.com', 'password123')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/login?redirect=false'),
        expect.objectContaining({
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/json' },
        }),
      )
      const body = JSON.parse((mockFetch as jest.Mock).mock.calls[0][1].body as string)
      expect(body.username).toBe('user@example.com')
      expect(body.password).toBe('password123')
    })

    it('does not expose tokens to the browser on BFF success', async () => {
      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ ok: true, code: 'one-time-code' }),
        }),
      )

      const result = await login('user@example.com', 'password123')
      // The BFF keeps tokens in its signed session — the SPA never sees them.
      expect(result.access_token).toBe('')
      expect(result.refresh_token).toBe('')
    })

    it('falls back to the backend password grant when no BFF is present (404)', async () => {
      const mockFetch = jest
        .fn()
        // First call: BFF endpoint missing
        .mockResolvedValueOnce({ ok: false, status: 404 })
        // Second call: direct backend password grant
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ access_token: 'abc123', token_type: 'bearer' }),
        })
      global.fetch = mockFetch

      const result = await login('user@example.com', 'password123')

      expect(result.access_token).toBe('abc123')
      expect(mockFetch).toHaveBeenCalledTimes(2)
      const fallbackUrl = (mockFetch as jest.Mock).mock.calls[1][0] as string
      expect(fallbackUrl).toContain('/api/v1/login/access-token')
      const body = (mockFetch as jest.Mock).mock.calls[1][1].body as URLSearchParams
      expect(body.get('username')).toBe('user@example.com')
      expect(body.get('password')).toBe('password123')
    })

    it('throws the BFF error verbatim on rejected credentials', async () => {
      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: false,
          status: 400,
          text: () => Promise.resolve('Incorrect email or password'),
        }),
      )

      await expect(login('bad@example.com', 'wrong')).rejects.toThrow(
        'Incorrect email or password',
      )
    })
  })
})
