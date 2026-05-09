/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'

const mockUseAuth = jest.fn()
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
  }),
}))
jest.mock('@/context/auth-context', () => ({
  useAuth: (...args: unknown[]) => mockUseAuth(...args),
}))

describe('AuthGuard', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders children when authenticated', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      token: 'token',
      login: jest.fn(),
      logout: jest.fn(),
    })


    const AuthGuard = jest.requireMock('@/components/auth-guard').default
    render(
      <AuthGuard>
        <span data-testid="content">Protected content</span>
      </AuthGuard>,
    )
    expect(screen.getByTestId('content')).toBeInTheDocument()
  })

  it('shows loading placeholder when not authenticated', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: false,
      token: null,
      login: jest.fn(),
      logout: jest.fn(),
    })


    const AuthGuard = jest.requireMock('@/components/auth-guard').default
    render(
      <AuthGuard>
        <span>Secret</span>
      </AuthGuard>,
    )
    expect(screen.getByText('Loading...')).toBeInTheDocument()
    expect(screen.queryByText('Secret')).not.toBeInTheDocument()
  })

  it('redirects to /login when not authenticated', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: false,
      token: null,
      login: jest.fn(),
      logout: jest.fn(),
    })

    const push = jest.fn()

    jest.spyOn(jest.requireMock('next/navigation'), 'useRouter').mockReturnValue({ push })


    const AuthGuard = jest.requireMock('@/components/auth-guard').default
    render(<AuthGuard><span>Secret</span></AuthGuard>)
    expect(push).toHaveBeenCalledWith('/login')
  })
})
