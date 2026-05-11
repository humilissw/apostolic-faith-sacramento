/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'

const mockUseAuth = jest.fn()
const mockRouter = { push: jest.fn() }
jest.mock('next/navigation', () => ({
  useRouter: () => mockRouter,
}))
jest.mock('@/context/auth-context', () => ({
  useAuth: (...args: unknown[]) => mockUseAuth(...args),
}))
jest.mock('@/context/feature-flag-context', () => ({
  useFeatureFlag: jest.fn(() => true),
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

    const AuthGuard = jest.requireActual('@/components/auth-guard').default
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

    const AuthGuard = jest.requireActual('@/components/auth-guard').default
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

    mockRouter.push.mockClear()

    const AuthGuard = jest.requireActual('@/components/auth-guard').default
    render(<AuthGuard><span>Secret</span></AuthGuard>)
    expect(mockRouter.push).toHaveBeenCalledWith('/login')
  })
})
