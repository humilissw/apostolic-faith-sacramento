/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen, fireEvent } from '@testing-library/react'
import DonationForm from '@/components/donation-form'

const mockUseAuth = jest.fn()
jest.mock('@/context/auth-context', () => ({
  useAuth: (...args: unknown[]) => mockUseAuth(...args),
}))

jest.mock('@/lib/api', () => ({
  createPaymentIntent: jest.fn().mockResolvedValue({
    client_secret: 'pi_secret_xyz',
    payment_intent_id: 'pi_test123',
  }),
  createSubscription: jest.fn().mockResolvedValue({
    client_secret: 'cs_secret_xyz',
    type: 'checkout',
    checkout_url: 'https://checkout.stripe.com/test',
  }),
  fetchDonationConfigs: jest.fn().mockResolvedValue([]),
}))

jest.mock('@stripe/stripe-js', () => ({
  loadStripe: jest.fn().mockResolvedValue({
    confirmCardPayment: jest.fn().mockResolvedValue({
      error: null,
      paymentIntent: { id: 'pi_test123', status: 'succeeded' },
    }),
  }),
}))

describe('DonationForm', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    // Default: probe settled, not authenticated -> guest fields visible
    mockUseAuth.mockReturnValue({ isAuthenticated: false, isLoadingToken: false })
  })

  it('renders with preset amounts', () => {
    render(<DonationForm />)
    expect(screen.getByText('Make a Donation')).toBeInTheDocument()
    expect(screen.getByText('$10')).toBeInTheDocument()
    expect(screen.getByText('$25')).toBeInTheDocument()
    expect(screen.getByText('$50')).toBeInTheDocument()
  })

  it('selects preset amount on click', () => {
    render(<DonationForm />)
    fireEvent.click(screen.getByText('$50'))
    expect(screen.getByLabelText('Custom Amount')).toHaveValue(50)
  })

  it('toggles between one-time and recurring', () => {
    render(<DonationForm />)
    const recurringRadio = screen.getByRole('radio', { name: /monthly/i })
    fireEvent.click(recurringRadio)
    expect(recurringRadio).toBeChecked()
  })

  it('shows guest fields when not authenticated', () => {
    render(<DonationForm />)
    expect(screen.getByLabelText(/name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
  })

  it('hides guest fields when authenticated', () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true, isLoadingToken: false })
    render(<DonationForm />)
    expect(screen.queryByLabelText(/^name$/i)).not.toBeInTheDocument()
    expect(screen.queryByLabelText(/email/i)).not.toBeInTheDocument()
  })

  // it('shows success message after payment', async () => {
  //   const onSuccess = jest.fn()
  //   render(<DonationForm onSuccess={onSuccess} />)
  //   const donateButton = screen.getByRole('button', { name: /Donate/i })

  //   fireEvent.click(donateButton)

  //   await waitFor(() => {
  //     expect(screen.getByTestId('success-title')).toBeInTheDocument()
  //   })

  //   await waitFor(() => {
  //     expect(onSuccess).toHaveBeenCalledWith('pi_test123')
  //   })
  // })
})
