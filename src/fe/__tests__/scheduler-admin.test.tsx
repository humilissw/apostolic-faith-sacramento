/** @jest-environment jsdom */

import SchedulerAdminPage from '@/app/(main)/scheduler-admin/page'
import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'

jest.mock('@/lib/api', () => ({
  fetchAssignments: jest.fn().mockResolvedValue({ data: [], count: 0 }),
  fetchUsersWithScopes: jest.fn().mockResolvedValue({ data: [], count: 0 }),
  fetchMyTimeOffRequests: jest.fn().mockResolvedValue({ data: [], count: 0 }),
  deleteAssignment: jest.fn(),
}))

describe('SchedulerAdminPage', () => {
  it('renders a heading', async () => {
    render(<SchedulerAdminPage />)
    await new Promise((r) => setTimeout(r, 100))
    expect(screen.getByText(/Scheduler Admin/i)).toBeInTheDocument()
  })
})
