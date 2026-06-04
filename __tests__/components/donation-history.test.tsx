/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen, waitFor } from '@testing-library/react'
import DonationHistory from '@/components/donation-history'

jest.mock('@/lib/api', () => ({
  fetchUserPayments: jest.fn().mockResolvedValue({
    data: [
      {
        id: 'pay_1',
        amount_cents: 5000,
        currency: 'usd',
        status: 'succeeded',
        donor_email: 'test@example.com',
        donor_name: 'Test User',
        receipt_url: 'https://stripe.com/receipt/123',
        created_on: '2026-01-15T00:00:00Z',
        stripe_payment_intent_id: 'pi_x',
        stripe_subscription_id: null,
        updated_on: null,
      },
    ],
    count: 1,
  }),
}))

describe('DonationHistory', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders payment entries', async () => {
    render(<DonationHistory />)
    await waitFor(() => {
      expect(screen.getByText('$50.00')).toBeInTheDocument()
    })
    expect(screen.getByText('succeeded')).toBeInTheDocument()
  })

  it('shows receipt link when available', async () => {
    render(<DonationHistory />)
    await waitFor(() => {
      expect(screen.getByText('Receipt')).toBeInTheDocument()
    })
  })
})
