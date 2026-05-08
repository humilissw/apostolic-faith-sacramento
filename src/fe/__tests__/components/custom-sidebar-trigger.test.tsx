/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen, fireEvent } from '@testing-library/react'
import CustomSidebarTrigger from '@/components/custom-sidebar-trigger'
import * as sidebar from '@/components/ui/sidebar'

jest.mock('@/components/ui/sidebar', () => ({
  useSidebar: jest.fn(() => ({ toggleSidebar: jest.fn() })),
}))

describe('CustomSidebarTrigger', () => {
  it('renders the menu icon when state is false', () => {
    ;(sidebar.useSidebar as jest.Mock).mockReturnValue({ toggleSidebar: jest.fn() })
    render(<CustomSidebarTrigger state={false} />)
    const trigger = screen.getByRole('button')
    expect(trigger).toHaveAttribute('aria-label', 'Open Menu')
  })

  it('renders the close icon when state is true', () => {
    ;(sidebar.useSidebar as jest.Mock).mockReturnValue({ toggleSidebar: jest.fn() })
    render(<CustomSidebarTrigger state={true} />)
    const trigger = screen.getByRole('button')
    expect(trigger).toHaveAttribute('aria-label', 'Close Menu')
  })

  it('calls toggleSidebar when clicked', () => {
    const toggleMock = jest.fn()
    ;(sidebar.useSidebar as jest.Mock).mockReturnValue({ toggleSidebar: toggleMock })
    const { container } = render(<CustomSidebarTrigger state={false} />)
    const trigger = screen.getByRole('button')
    fireEvent.click(trigger)
    expect(toggleMock).toHaveBeenCalledTimes(1)
  })
})
