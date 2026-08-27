/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen, fireEvent } from '@testing-library/react'
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
    // Profile dropdown trigger is visible; "Log out" item appears when opened
    const trigger = screen.getByRole('button', { name: /user menu/i })
    expect(trigger).toBeInTheDocument()
    // Radix opens the menu on pointerdown (jsdom lacks event.button) — use the keyboard path
    fireEvent.keyDown(trigger, { key: 'Enter' })
    expect(screen.getByRole('menuitem', { name: /log out/i })).toBeInTheDocument()
  })

  it('does not render Login button when logged in', () => {
    render(<Navbar />)
    expect(screen.queryByRole('button', { name: /^login$/i })).not.toBeInTheDocument()
  })

  it('renders public nav links', () => {
    render(<Navbar />)
    // Links appear in both the desktop bar and the mobile sidebar (jsdom shows both)
    for (const title of ['Home', 'Our Beliefs', 'Media', 'Donate', 'Contact Us']) {
      expect(screen.getAllByText(title).length).toBeGreaterThan(0)
    }
  })

  it('renders authenticated links', () => {
    render(<Navbar />)
    expect(screen.getAllByText('Video Uploads').length).toBeGreaterThan(0)
  })

  it('renders scheduler links when user has scheduler:admin scope', () => {
    render(<Navbar />)
    for (const title of ['Scheduler Admin', 'Scheduler Calendar', 'My Scheduler']) {
      expect(screen.getAllByText(title).length).toBeGreaterThan(0)
    }
  })

  it('renders user profile section when authenticated', () => {
    render(<Navbar />)
    // Profile dropdown is rendered for authenticated users (icon trigger + My Account label)
    expect(screen.getByRole('button', { name: /user menu/i })).toBeInTheDocument()
    fireEvent.keyDown(screen.getByRole('button', { name: /user menu/i }), { key: 'Enter' })
    expect(screen.getByText(/my account/i)).toBeInTheDocument()
  })
})
