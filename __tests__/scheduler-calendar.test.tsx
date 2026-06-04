/** @jest-environment jsdom */

import SchedulerCalendarPage from '@/app/(main)/scheduler-calendar/page'
import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'

jest.mock('@/lib/api', () => ({
  fetchCalendarAssignments: jest.fn().mockResolvedValue({ data: [], count: 0 }),
}))

describe('SchedulerCalendarPage', () => {
  it('renders a heading', async () => {
    render(<SchedulerCalendarPage />)
    await new Promise((r) => setTimeout(r, 100))
    expect(screen.getByText(/Scheduler Calendar/i)).toBeInTheDocument()
  })
})
