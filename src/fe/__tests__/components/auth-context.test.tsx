/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen, fireEvent } from '@testing-library/react'
import { AuthProvider, useAuth } from '@/context/auth-context'

function TestChild({ onAuth }: { onAuth?: (ctx: ReturnType<typeof useAuth>) => void }) {
  const auth = useAuth()
  if (onAuth) onAuth(auth)
  return (
    <div>
      <span data-testid="isAuthenticated">{String(auth.isAuthenticated)}</span>
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
    <AuthProvider>
      {ui}
    </AuthProvider>,
  )
}

describe('AuthProvider', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('starts logged out when no auth cookie', () => {
    renderWithProvider(<TestChild />)
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false')
  })

  it('shows authenticated when localStorage has access_token', () => {
    localStorage.setItem('access_token', 'fake')
    renderWithProvider(<TestChild />)
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true')
  })

  it('logs in by setting state', () => {
    renderWithProvider(<TestChild />)
    fireEvent.click(screen.getByTestId('loginBtn'))
    // login() sets an expiry estimate (10 min)
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true')
  })

  it('provides isAuthenticated as true when cookie exists', () => {
    document.cookie = 'access_token=test; path=/'
    renderWithProvider(<TestChild />)
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true')
  })
})
