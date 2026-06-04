/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { VersionSwitcher } from '@/components/version-switcher'

jest.mock('@/components/ui/sidebar', () => ({
  SidebarMenu: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SidebarMenuItem: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SidebarMenuButton: ({ children }: { children: React.ReactNode }) => (
    <button data-testid="trigger">{children}</button>
  ),
  useSidebar: jest.fn(() => ({})),
}))

jest.mock('@/components/ui/dropdown-menu', () => ({
  DropdownMenu: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  DropdownMenuContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  DropdownMenuItem: ({ children, onSelect }: { children: React.ReactNode; onSelect?: () => void }) => (
    <button data-testid="version-item" onClick={onSelect}>{children}</button>
  ),
  DropdownMenuTrigger: ({ children }: { children: React.ReactNode }) => <>{children}</>,
}))

describe('VersionSwitcher', () => {
  it('renders the default version in the trigger', () => {
    render(<VersionSwitcher versions={['1.0', '2.0']} defaultVersion="1.0" />)
    expect(screen.getByTestId('trigger')).toBeInTheDocument()
  })

  it('renders all version options in the dropdown', () => {
    render(<VersionSwitcher versions={['1.0', '2.0']} defaultVersion="1.0" />)
    expect(screen.getAllByText('v1.0')).toHaveLength(2)
    expect(screen.getByText('v2.0')).toBeInTheDocument()
  })

  it('selects a version when its dropdown item is clicked', async () => {
    render(<VersionSwitcher versions={['1.0', '2.0']} defaultVersion="1.0" />)
    const dropdownItems = screen.getAllByTestId('version-item')
    const v2Item = dropdownItems.find((btn) => btn.textContent?.trim() === 'v2.0')
    fireEvent.click(v2Item!)
    await waitFor(() => {
      expect(screen.getByTestId('trigger')).toHaveTextContent(/v2\.0/)
    })
  })

  it('matches snapshot', () => {
    const { container } = render(<VersionSwitcher versions={['1.0', '2.0', '3.0']} defaultVersion="1.0" />)
    expect(container).toMatchSnapshot()
  })
})
