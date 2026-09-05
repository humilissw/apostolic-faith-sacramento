/** @jest-environment jsdom */

import { login } from '@/lib/api'

describe('API utilities', () => {
  beforeEach(() => {
    jest.restoreAllMocks()
  })

  describe('login (backend password grant)', () => {
    it('sends a form-encoded POST to the backend login/access-token endpoint', async () => {
      const mockFetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          json: () => Promise.resolve({ access_token: 'abc123', token_type: 'bearer' }),
        }),
      )
      global.fetch = mockFetch

      await login('user@example.com', 'password123')

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/login/access-token'),
        expect.objectContaining({
          method: 'POST',
          credentials: 'include',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        }),
      )
      const body = (mockFetch as jest.Mock).mock.calls[0][1].body as URLSearchParams
      expect(body.get('username')).toBe('user@example.com')
      expect(body.get('password')).toBe('password123')
    })

    it('returns the tokens from the backend response', async () => {
      global.fetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve({ access_token: 'abc123', refresh_token: 'r1', token_type: 'bearer' }),
        }),
      )

      const result = await login('user@example.com', 'password123')
      expect(result.access_token).toBe('abc123')
      expect(result.refresh_token).toBe('r1')
    })

    it('throws the backend error verbatim on rejected credentials', async () => {
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
