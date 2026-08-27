/** @jest-environment jsdom */

import DonatePage from '@/app/(main)/donate/page'
import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'

const mockUseAuth = jest.fn()
jest.mock('@/context/auth-context', () => ({
  useAuth: (...args: unknown[]) => mockUseAuth(...args),
}))

jest.mock('@/components/donation-form', () => {
  return function MockDonationForm() {
    return <div data-testid="donation-form">DonationForm</div>
  }
})

jest.mock('@/components/donation-history', () => {
  return function MockDonationHistory() {
    return <div data-testid="donation-history">DonationHistory</div>
  }
})

describe('DonatePage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    // Default: probe settled, not authenticated
    mockUseAuth.mockReturnValue({ isAuthenticated: false, isLoadingToken: false })
  })

  it('renders the donation heading', () => {
    render(<DonatePage />)
    expect(screen.getByText(/support apostolic faith/i)).toBeInTheDocument()
  })

  it('renders the donation form', () => {
    render(<DonatePage />)
    expect(screen.getByTestId('donation-form')).toBeInTheDocument()
  })

  it('hides donation history when not authenticated', () => {
    render(<DonatePage />)
    expect(screen.queryByTestId('donation-history')).not.toBeInTheDocument()
  })

  it('shows donation history when authenticated', () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true, isLoadingToken: false })
    render(<DonatePage />)
    expect(screen.getByTestId('donation-history')).toBeInTheDocument()
  })

  it('holds off on donation history while the auth probe is in flight', () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: false, isLoadingToken: true })
    render(<DonatePage />)
    expect(screen.queryByTestId('donation-history')).not.toBeInTheDocument()
  })
})
