/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'

jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}))

jest.mock('@/context/auth-context', () => ({
  useAuth: jest.fn(() => ({
    isAuthenticated: true,
    token: 'fake-token',
    login: jest.fn(),
    logout: jest.fn(),
  })),
}))

function TestChild({ children }: { children: React.ReactNode }) {
  return <>{children}</>
}

describe('AuthGuard', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders children when authenticated', () => {
    const { useAuth } = require('@/context/auth-context')
    useAuth.mockReturnValue({
      isAuthenticated: true,
      token: 'token',
      login: jest.fn(),
      logout: jest.fn(),
    })

    const AuthGuard = require('@/components/auth-guard').default
    render(
      <AuthGuard>
        <span data-testid="content">Protected content</span>
      </AuthGuard>,
    )
    expect(screen.getByTestId('content')).toBeInTheDocument()
  })

  it('shows loading placeholder when not authenticated', () => {
    const { useAuth } = require('@/context/auth-context')
    useAuth.mockReturnValue({
      isAuthenticated: false,
      token: null,
      login: jest.fn(),
      logout: jest.fn(),
    })

    const AuthGuard = require('@/components/auth-guard').default
    render(
      <AuthGuard>
        <span>Secret</span>
      </AuthGuard>,
    )
    expect(screen.getByText('Loading...')).toBeInTheDocument()
    expect(screen.queryByText('Secret')).not.toBeInTheDocument()
  })

  it('redirects to /login when not authenticated', () => {
    const { useAuth } = require('@/context/auth-context')
    useAuth.mockReturnValue({
      isAuthenticated: false,
      token: null,
      login: jest.fn(),
      logout: jest.fn(),
    })

    const push = jest.fn()
    jest.spyOn(require('next/navigation'), 'useRouter').mockReturnValue({ push })

    const AuthGuard = require('@/components/auth-guard').default
    render(<AuthGuard><span>Secret</span></AuthGuard>)
    expect(push).toHaveBeenCalledWith('/login')
  })
})
