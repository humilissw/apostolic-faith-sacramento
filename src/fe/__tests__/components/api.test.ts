/** @jest-environment jsdom */

import { login } from '@/lib/api'

describe('API utilities', () => {
  beforeEach(() => {
    jest.restoreAllMocks()
  })

  describe('login', () => {
    it('sends a POST request with form-encoded data', async () => {
      const mockFetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ access_token: 'jwt-token', token_type: 'bearer' }),
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
    })

    it('returns the access token from the response', async () => {
      const mockFetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ access_token: 'abc123', token_type: 'bearer' }),
        }),
      )
      global.fetch = mockFetch

      const result = await login('user@example.com', 'password123')
      expect(result.access_token).toBe('abc123')
    })

    it('throws on a failed response', async () => {
      const mockFetch = jest.fn(() =>
        Promise.resolve({
          ok: false,
          status: 400,
          text: () => Promise.resolve('Incorrect email or password'),
        }),
      )
      global.fetch = mockFetch

      await expect(login('bad@example.com', 'wrong')).rejects.toThrow('Incorrect email or password')
    })

    it('appends username and password to the form body', async () => {
      const mockFetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ access_token: 'token', token_type: 'bearer' }),
        }),
      )
      global.fetch = mockFetch

      await login('test@example.com', 'secret')

      expect(mockFetch).toHaveBeenCalled()
      const body = (mockFetch as jest.Mock).mock.calls[0][1].body as URLSearchParams
      expect(body.get('username')).toBe('test@example.com')
      expect(body.get('password')).toBe('secret')
    })
  })
})
