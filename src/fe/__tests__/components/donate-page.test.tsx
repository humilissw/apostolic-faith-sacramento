/** @jest-environment jsdom */

import DonatePage from '@/app/(main)/donate/page'
import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'

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
    // Default: not authenticated (no access_token cookie)
    document.cookie = 'access_token=; max-age=0; path=/'
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
    document.cookie = 'access_token=fake; path=/'
    render(<DonatePage />)
    expect(screen.getByTestId('donation-history')).toBeInTheDocument()
  })
})
