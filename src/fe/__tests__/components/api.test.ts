/** @jest-environment jsdom */

import { login, getAuthToken, setAuthToken, clearAuthToken } from '@/lib/api'

describe('API utilities', () => {
  beforeEach(() => {
    localStorage.clear()
    jest.restoreAllMocks()
  })

  describe('token helpers', () => {
    it('returns null for getAuthToken when nothing is set', () => {
      expect(getAuthToken()).toBeNull()
    })

    it('returns the stored token from localStorage', () => {
      setAuthToken('test-token')
      expect(getAuthToken()).toBe('test-token')
    })

    it('clears the token from localStorage', () => {
      setAuthToken('test-token')
      clearAuthToken()
      expect(getAuthToken()).toBeNull()
    })

    it('sets the token in localStorage', () => {
      setAuthToken('my-token')
      expect(localStorage.getItem('auth_token')).toBe('my-token')
    })
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

    it('uses the configured API base URL', async () => {
      const mockFetch = jest.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ access_token: 'token', token_type: 'bearer' }),
        }),
      )
      global.fetch = mockFetch

      await login('user@example.com', 'password123')

      expect(mockFetch).toHaveBeenCalled()
      const calledUrl = (mockFetch as jest.Mock).mock.calls[0][0]
      expect(calledUrl).toContain('/api/v1/login/access-token')
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
