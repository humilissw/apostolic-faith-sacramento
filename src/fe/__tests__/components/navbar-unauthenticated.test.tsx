/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import Navbar from '@/components/navbar'
import { useFeatureFlag } from '@/context/feature-flag-context'

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

jest.mock('@/context/feature-flag-context', () => ({
  useFeatureFlag: jest.fn(() => true),
}))

describe('Navbar (unauthenticated)', () => {
  it('renders the AFC brand', () => {
    render(<Navbar />)
    expect(screen.getByAltText('Apostolic Faith Church Logo')).toBeInTheDocument()
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
    // Links appear in both the desktop bar and the mobile sidebar (jsdom shows both)
    for (const title of ['Home', 'Our Beliefs', 'Sermons', 'Media', 'Donate', 'Contact Us']) {
      expect(screen.getAllByText(title).length).toBeGreaterThan(0)
    }
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

describe('Navbar (feature flags)', () => {
  // Flag-aware mock: default everything on, then flip individual flags off.
  const disabledFlags = new Set<string>()
  beforeEach(() => disabledFlags.clear())

  function renderWithFlagOff(flagName: string) {
    disabledFlags.add(flagName)
    ;(useFeatureFlag as jest.Mock).mockImplementation((name: string) => !disabledFlags.has(name))
    render(<Navbar />)
  }

  it('hides Events when enable_events is off', () => {
    renderWithFlagOff('enable_events')
    expect(screen.queryByText('Events')).not.toBeInTheDocument()
    // Other public links still render
    expect(screen.getAllByText('Home').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Media').length).toBeGreaterThan(0)
  })

  it('shows Events when enable_events is on', () => {
    ;(useFeatureFlag as jest.Mock).mockImplementation(() => true)
    render(<Navbar />)
    expect(screen.getAllByText('Events').length).toBeGreaterThan(0)
  })
})
