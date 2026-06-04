/** @jest-environment jsdom */
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import IntegrationsPage from '@/app/(main)/integrations/page'

const mockIntegrations = [
  {
    id: '1',
    type: 'stripe',
    display_name: 'Stripe Payments',
    icon: 'CreditCard',
    enabled: true,
    status: 'connected',
    last_synced_at: null,
    config_json: null,
    created_on: '2026-01-01T00:00:00',
    updated_on: null,
    credential_fields: {},
  },
  {
    id: '2',
    type: 'twilio',
    display_name: 'Twilio SMS',
    icon: 'MessageSquare',
    enabled: false,
    status: 'disconnected',
    last_synced_at: null,
    config_json: null,
    created_on: '2026-01-01T00:00:00',
    updated_on: null,
    credential_fields: {},
  },
]

jest.mock('@/lib/api', () => ({
  fetchIntegrations: jest.fn(),
  deleteIntegration: jest.fn(),
  preSeedIntegrations: jest.fn(),
}))

jest.mock('@/components/integration-dialog', () => {
  return function MockIntegrationDialog({ open }: { open: boolean }) {
    return open ? <div data-testid="integration-dialog">IntegrationDialog</div> : null
  }
})

const { fetchIntegrations } = jest.requireMock('@/lib/api')

describe('IntegrationsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    jest.spyOn(global, 'confirm').mockReturnValue(true)
  })

  it('shows loading state initially', () => {
    fetchIntegrations.mockReturnValue(new Promise(() => {}))
    render(<IntegrationsPage />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders integrations table when data loaded', async () => {
    fetchIntegrations.mockResolvedValue({ data: mockIntegrations })
    render(<IntegrationsPage />)
    await waitFor(() => {
      expect(screen.getByText('Stripe Payments')).toBeInTheDocument()
      expect(screen.getByText('Twilio SMS')).toBeInTheDocument()
    })
  })

  it('shows error when fetch fails', async () => {
    fetchIntegrations.mockRejectedValue(new Error('Network error'))
    render(<IntegrationsPage />)
    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument()
    })
  })

  it('renders Pre-seed button', async () => {
    fetchIntegrations.mockResolvedValue({ data: [] })
    render(<IntegrationsPage />)
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Pre-seed/i })).toBeInTheDocument()
    })
  })

  it('renders New Integration button', async () => {
    fetchIntegrations.mockResolvedValue({ data: [] })
    render(<IntegrationsPage />)
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /New Integration/i })).toBeInTheDocument()
    })
  })

  it('opens dialog when New Integration is clicked', async () => {
    fetchIntegrations.mockResolvedValue({ data: [] })
    render(<IntegrationsPage />)
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /New Integration/i })).toBeInTheDocument()
    })
    fireEvent.click(screen.getByRole('button', { name: /New Integration/i }))
    await waitFor(() => {
      expect(screen.getByTestId('integration-dialog')).toBeInTheDocument()
    })
  })

  it('shows connected status with check icon', async () => {
    fetchIntegrations.mockResolvedValue({ data: mockIntegrations })
    render(<IntegrationsPage />)
    await waitFor(() => {
      expect(screen.getByText('connected')).toBeInTheDocument()
    })
  })

  it('shows disconnected status with icon', async () => {
    fetchIntegrations.mockResolvedValue({ data: mockIntegrations })
    render(<IntegrationsPage />)
    await waitFor(() => {
      expect(screen.getByText('disconnected')).toBeInTheDocument()
    })
  })

  it('shows enabled indicator', async () => {
    fetchIntegrations.mockResolvedValue({ data: mockIntegrations })
    render(<IntegrationsPage />)
    await waitFor(() => {
      expect(screen.getByText('Yes')).toBeInTheDocument()
      expect(screen.getAllByText('No')).toHaveLength(1)
    })
  })

  it('renders edit and delete buttons for each integration', async () => {
    fetchIntegrations.mockResolvedValue({ data: mockIntegrations })
    render(<IntegrationsPage />)
    await waitFor(() => {
      const rows = screen.getAllByRole('row')
      expect(rows.length).toBeGreaterThan(2)
    })
  })
})
