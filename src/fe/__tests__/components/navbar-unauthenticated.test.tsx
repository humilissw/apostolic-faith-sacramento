/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import Navbar from '@/components/navbar'

jest.mock('next/navigation', () => ({
  ...jest.requireActual('next/navigation'),
  usePathname: () => '/',
}))

jest.mock('@/context/auth-context', () => ({
  useAuth: jest.fn(() => ({
    isAuthenticated: false,
    token: null,
    login: jest.fn(),
    logout: jest.fn(),
    hasScope: jest.fn(() => false),
  })),
}))

describe('Navbar (unauthenticated)', () => {
  it('renders the AFC brand', () => {
    render(<Navbar />)
    expect(screen.getByText('AFC')).toBeInTheDocument()
  })

  it('renders a Login button', () => {
    render(<Navbar />)
    const loginBtn = screen.getByRole('button', { name: /login/i })
    expect(loginBtn).toBeInTheDocument()
  })

  it('does not render a Logout button', () => {
    render(<Navbar />)
    expect(screen.queryByRole('button', { name: /logout/i })).not.toBeInTheDocument()
  })

  it('renders public nav links', () => {
    render(<Navbar />)
    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Our Beliefs')).toBeInTheDocument()
    expect(screen.getByText('Sermons')).toBeInTheDocument()
    expect(screen.getByText('Media')).toBeInTheDocument()
    expect(screen.getByText('Donate')).toBeInTheDocument()
    expect(screen.getByText('Contact Us')).toBeInTheDocument()
  })

  it('does not render authenticated links', () => {
    render(<Navbar />)
    expect(screen.queryByText('Video Uploads')).not.toBeInTheDocument()
    expect(screen.queryByText('Scheduler Admin')).not.toBeInTheDocument()
    expect(screen.queryByText('User Management')).not.toBeInTheDocument()
  })

  it('does not render user profile section', () => {
    render(<Navbar />)
    // No user profile section for unauthenticated
    const signInText = screen.queryByText(/signed in/i)
    expect(signInText).not.toBeInTheDocument()
  })
})
