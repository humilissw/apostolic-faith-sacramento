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
    isAuthenticated: true,
    token: 'fake-token',
    login: jest.fn(),
    logout: jest.fn(),
    hasScope: jest.fn((scope: string) => scope === 'scheduler:admin'),
  })),
}))

jest.mock('@/context/feature-flag-context', () => ({
  useFeatureFlag: jest.fn(() => true),
}))

describe('Navbar (authenticated)', () => {
  it('renders the AFC brand', () => {
    render(<Navbar />)
    expect(screen.getByAltText('Apostolic Faith Church Logo')).toBeInTheDocument()
  })

  it('renders a Logout button when logged in', () => {
    render(<Navbar />)
    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument()
  })

  it('does not render Login button when logged in', () => {
    render(<Navbar />)
    expect(screen.queryByRole('button', { name: /login/i })).not.toBeInTheDocument()
  })

  it('renders public nav links', () => {
    render(<Navbar />)
    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Our Beliefs')).toBeInTheDocument()
    expect(screen.getByText('Media')).toBeInTheDocument()
    expect(screen.getByText('Donate')).toBeInTheDocument()
    expect(screen.getByText('Contact Us')).toBeInTheDocument()
  })

  it('renders authenticated links', () => {
    render(<Navbar />)
    expect(screen.getByText('Video Uploads')).toBeInTheDocument()
  })

  it('renders scheduler links when user has scheduler:admin scope', () => {
    render(<Navbar />)
    expect(screen.getByText('Scheduler Admin')).toBeInTheDocument()
    expect(screen.getByText('Scheduler Calendar')).toBeInTheDocument()
    expect(screen.getByText('My Scheduler')).toBeInTheDocument()
  })

  it('renders user profile section when authenticated', () => {
    render(<Navbar />)
    expect(screen.getByText(/signed in/i)).toBeInTheDocument()
  })
})
