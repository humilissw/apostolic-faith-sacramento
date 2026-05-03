/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen, waitFor, act } from '@testing-library/react'
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

jest.mock('@/lib/api', () => ({
  setRefreshToken: jest.fn(),
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
  })

  it('renders login complete message', async () => {
    window.history.pushState(
      {},
      '',
      '/google-callback?access_token=fake-jwt&refresh_token=fake-refresh',
    )

    await act(async () => {
      render(<GoogleCallbackPage />)
    })

    expect(screen.getByText('Completing Google sign-in...')).toBeInTheDocument()
  })

  it('completes login when tokens are present', async () => {
    window.history.pushState(
      {},
      '',
      '/google-callback?access_token=fake-jwt&refresh_token=fake-refresh',
    )

    await act(async () => {
      render(<GoogleCallbackPage />)
    })

    await act(async () => {
      jest.runAllTimers()
    })

    expect(mockLogin).toHaveBeenCalledWith('fake-jwt', 'fake-refresh')
    expect(mockLogout).not.toHaveBeenCalled()
  })

  it('shows error and redirects when tokens are missing', async () => {
    window.history.pushState({}, '', '/google-callback')

    await act(async () => {
      render(<GoogleCallbackPage />)
    })

    expect(
      screen.getByText('Missing tokens from authentication server'),
    ).toBeInTheDocument()

    await act(async () => {
      jest.runAllTimers()
    })

    expect(mockPush).toHaveBeenCalledWith('/login')
  })
})
