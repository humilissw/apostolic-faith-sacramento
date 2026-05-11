/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen, act } from '@testing-library/react'
import React from 'react'

jest.useFakeTimers()

const mockPush = jest.fn()
jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  useRouter: () => ({ push: mockPush }),
  useSearchParams: () => ({
    get: (key: string) => {
      const params = new URLSearchParams(window.location.search)
      return params.get(key)
    },
  }),
}))

const mockLogin = jest.fn()
const mockLogout = jest.fn()
jest.mock('@/context/auth-context', () => ({
  useAuth: jest.fn(() => ({ login: mockLogin, logout: mockLogout })),
}))

import GoogleCallbackPage from '@/app/(auth)/google-callback/page'

describe('GoogleCallbackPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockPush.mockClear()
    mockLogin.mockClear()
    mockLogout.mockClear()
    jest.useFakeTimers()
    window.history.pushState({}, '', '/')
    // Mock /auth/me to return success when cookie is present
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ email: 'test@test.com', is_superuser: false }),
      }),
    )
  })

  it('renders login complete message', async () => {
    window.history.pushState({}, '', '/google-callback')

    await act(async () => {
      render(<GoogleCallbackPage />)
    })

    expect(screen.getByText('Completing Google sign-in...')).toBeInTheDocument()
  })

  it('completes login when /auth/me returns valid user', async () => {
    window.history.pushState({}, '', '/google-callback')

    await act(async () => {
      render(<GoogleCallbackPage />)
    })

    await act(async () => {
      jest.runAllTimers()
    })

    expect(mockLogin).toHaveBeenCalled()
    expect(mockPush).toHaveBeenCalledWith('/')
  })

  it('shows error and redirects when /auth/me fails', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({ ok: false, status: 401, text: () => Promise.resolve('') }),
    )

    window.history.pushState({}, '', '/google-callback')

    await act(async () => {
      render(<GoogleCallbackPage />)
    })

    expect(
      screen.getByText('Authentication failed — cookies invalid'),
    ).toBeInTheDocument()

    await act(async () => {
      jest.runAllTimers()
    })

    expect(mockPush).toHaveBeenCalledWith('/login')
  })
})
