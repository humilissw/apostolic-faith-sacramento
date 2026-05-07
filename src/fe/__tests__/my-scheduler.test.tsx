/** @jest-environment jsdom */

import MySchedulerPage from '@/app/(main)/my-scheduler/page'
import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'

jest.mock('@/lib/api', () => ({
  fetchMyAssignments: jest.fn().mockResolvedValue({ data: [], count: 0 }),
}))

describe('MySchedulerPage', () => {
  it('renders a heading', async () => {
    render(<MySchedulerPage />)
    await new Promise((r) => setTimeout(r, 100))
    expect(screen.getByText(/My Scheduler/i)).toBeInTheDocument()
  })
})
