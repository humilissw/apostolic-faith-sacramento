/** @jest-environment jsdom */

import MySchedulerPage from '@/app/(main)/my-scheduler/page'
import '@testing-library/jest-dom'
import { render, screen, waitFor } from '@testing-library/react'

jest.mock('@/lib/api', () => ({
  fetchMyAssignments: jest.fn().mockResolvedValue({ data: [], count: 0 }),
}))

const { fetchMyAssignments } = jest.requireMock('@/lib/api')

jest.mock('sonner', () => ({
  toast: { success: jest.fn(), error: jest.fn() },
}))

jest.mock('@/components/auth-guard', () => ({
  default: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

jest.mock('@/components/scope-guard', () => ({
  default: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

jest.mock('@/components/feature-flag-guard', () => ({
  default: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

jest.mock('@/components/video-upload-dialog', () => {
  return function MockDialog({ open }: { open: boolean }) {
    return open ? <div data-testid="dialog">Dialog</div> : null
  }
})

const mockAssignments = [
  {
    id: 'assign-1',
    user_id: 'user-123',
    event_date: '2026-07-01T10:00:00',
    type: 'music',
    role: 'Worship Leader',
    instrument: 'Guitar',
    notes: 'First song',
    created_on: '2026-06-01T00:00:00',
    updated_on: null,
  },
  {
    id: 'assign-2',
    user_id: 'user-123',
    event_date: '2026-07-15T14:00:00',
    type: 'service',
    role: 'Usher',
    instrument: null,
    notes: null,
    created_on: '2026-06-01T00:00:00',
    updated_on: null,
  },
]

describe('MySchedulerPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders a heading', async () => {
    render(<MySchedulerPage />)
    await new Promise((r) => setTimeout(r, 100))
    expect(screen.getByText(/My Scheduler/i)).toBeInTheDocument()
  })

  it('renders empty state when no assignments', async () => {
    fetchMyAssignments.mockResolvedValue({ data: [], count: 0 })
    render(<MySchedulerPage />)
    await waitFor(() => {
      expect(screen.getByText('No assignments yet')).toBeInTheDocument()
    })
  })

  it('renders assignments in the table', async () => {
    fetchMyAssignments.mockResolvedValue({ data: mockAssignments, count: mockAssignments.length })
    render(<MySchedulerPage />)
    await waitFor(() => {
      expect(screen.getByText('Worship Leader')).toBeInTheDocument()
      expect(screen.getByText('Usher')).toBeInTheDocument()
      expect(screen.getByText('Guitar')).toBeInTheDocument()
    })
  })
})
