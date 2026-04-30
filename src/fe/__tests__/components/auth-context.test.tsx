/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { AuthProvider, useAuth } from '@/context/auth-context'

function TestChild({ onAuth }: { onAuth?: (ctx: ReturnType<typeof useAuth>) => void }) {
  const auth = useAuth()
  if (onAuth) onAuth(auth)
  return (
    <div>
      <span data-testid="isAuthenticated">{String(auth.isAuthenticated)}</span>
      <span data-testid="token">{auth.token ?? 'null'}</span>
      <button data-testid="loginBtn" onClick={() => auth.login('new-token')}>
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
    localStorage.clear()
  })

  it('starts logged out when no token in localStorage', () => {
    renderWithProvider(<TestChild />)
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false')
    expect(screen.getByTestId('token')).toHaveTextContent('null')
  })

  it('restores token from localStorage on mount', () => {
    localStorage.setItem('auth_token', 'existing-token')
    renderWithProvider(<TestChild />)
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true')
    expect(screen.getByTestId('token')).toHaveTextContent('existing-token')
  })

  it('logs in and sets token in localStorage', () => {
    renderWithProvider(<TestChild />)
    fireEvent.click(screen.getByTestId('loginBtn'))
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true')
    expect(screen.getByTestId('token')).toHaveTextContent('new-token')
    expect(localStorage.getItem('auth_token')).toBe('new-token')
  })

  it('logs out and clears token from localStorage', () => {
    localStorage.setItem('auth_token', 'existing-token')
    renderWithProvider(<TestChild />)
    fireEvent.click(screen.getByTestId('loginBtn'))
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true')
    fireEvent.click(screen.getByTestId('logoutBtn'))
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('false')
    expect(screen.getByTestId('token')).toHaveTextContent('null')
    expect(localStorage.getItem('auth_token')).toBeNull()
  })

  it('provides isAuthenticated as true when token exists', () => {
    localStorage.setItem('auth_token', 'test-token')
    renderWithProvider(<TestChild />)
    expect(screen.getByTestId('isAuthenticated')).toHaveTextContent('true')
  })
})
