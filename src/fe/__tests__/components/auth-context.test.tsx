/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen, act } from '@testing-library/react'
import { AuthProvider, useAuth } from '@/context/auth-context'

const mockFetchMe = jest.fn()
const mockLogout = jest.fn()
const mockRefreshToken = jest.fn()

jest.mock('@/lib/api', () => ({
  fetchMe: (...args: unknown[]) => mockFetchMe(...args),
  logout: (...args: unknown[]) => mockLogout(...args),
  refreshToken: (...args: unknown[]) => mockRefreshToken(...args),
}))

function TestChild({ onAuth }: { onAuth?: (ctx: ReturnType<typeof useAuth>) => void }) {
  const auth = useAuth()
  if (onAuth) onAuth(auth)
  return (
    <div>
      <span data-testid="isAuthenticated">{String(auth.isAuthenticated)}</span>
      <span data-testid="isLoadingToken">{String(auth.isLoadingToken)}</span>
      <button data-testid="loginBtn" onClick={() => auth.login()}>
        Login
      </button>
      <button data-testid="logoutBtn" onClick={() => auth.logout()}>
        Logout
      </button>
    </div>
  )
}

function renderWithProvider(ui: React.ReactNode) {
  return render(
    <AuthProvider>{ui}</AuthProvider>,
  )
}

describe('AuthProvider', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockLogout.mockResolvedValue(undefined)
    mockRefreshToken.mockResolvedValue({})
    // Default: no session
    mockFetchMe.mockResolvedValue(null)
  })

  it('starts checking, then resolves to logged out when /auth/me returns null', async () => {
    let ctx: ReturnType<typeof useAuth> | undefined
    renderWithProvider(<TestChild onAuth={(c) => (ctx = c)} />)

    // While the probe is in flight we must NOT claim "logged out" yet —
    // guards key off isLoadingToken to avoid redirecting valid sessions.
    expect(ctx!.isLoadingToken).toBe(true)
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false')

    await act(async () => {})
    expect(mockFetchMe).toHaveBeenCalled()
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false')
    expect(screen.getByTestId('isLoadingToken')).toHaveTextContent('false')
  })

  it('shows authenticated when /auth/me returns a user', async () => {
    mockFetchMe.mockResolvedValue({ email: 'admin@afc.org', assigned_scopes: ['api:all'] })

    renderWithProvider(<TestChild />)
    await act(async () => {})

    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true')
  })

  it('login() re-probes and flips state once the session exists', async () => {
    mockFetchMe.mockResolvedValueOnce(null).mockResolvedValue({ email: 'a@b.c' })

    let ctx: ReturnType<typeof useAuth> | undefined
    renderWithProvider(<TestChild onAuth={(c) => (ctx = c)} />)
    await act(async () => {})
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false')

    await act(async () => {
      ctx!.login()
    })
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true')
  })

  it('logout() calls the BFF logout and clears state', async () => {
    mockFetchMe.mockResolvedValue({ email: 'a@b.c' })
    let ctx: ReturnType<typeof useAuth> | undefined
    renderWithProvider(<TestChild onAuth={(c) => (ctx = c)} />)
    await act(async () => {})

    // window.location.assign('/login') runs for real in jsdom (navigation is a
    // no-op there); we assert the state effects, which are what matter.
    await act(async () => {
      await ctx!.logout()
    })

    expect(mockLogout).toHaveBeenCalled()
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false')
  })

  it('hasScope reflects the scopes from /auth/me (superuser bypasses)', async () => {
    mockFetchMe.mockResolvedValue({ email: 'a@b.c', assigned_scopes: ['scheduler:admin'] })
    let ctx: ReturnType<typeof useAuth> | undefined
    renderWithProvider(<TestChild onAuth={(c) => (ctx = c)} />)
    await act(async () => {})

    expect(ctx!.hasScope('scheduler:admin')).toBe(true)
    expect(ctx!.hasScope('superuser')).toBe(false)
  })

  it('refreshAccessToken() delegates to the BFF refresh endpoint', async () => {
    mockFetchMe.mockResolvedValue({ email: 'a@b.c' })
    let ctx: ReturnType<typeof useAuth> | undefined
    renderWithProvider(<TestChild onAuth={(c) => (ctx = c)} />)
    await act(async () => {})

    await act(async () => {
      await ctx!.refreshAccessToken()
    })
    expect(mockRefreshToken).toHaveBeenCalled()
  })
})
