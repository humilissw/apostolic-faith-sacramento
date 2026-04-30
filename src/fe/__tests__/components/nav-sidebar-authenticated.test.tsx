/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { NavSidebar } from '@/components/nav-sidebar'

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn(() => ({
    matches: false,
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  })),
})

jest.mock('@/components/ui/sidebar', () => ({
  useSidebar: jest.fn(() => ({
    state: 'expanded',
    open: true,
    setOpen: jest.fn(),
    openMobile: true,
    setOpenMobile: jest.fn(),
    isMobile: false,
    toggleSidebar: jest.fn(),
  })),
  Sidebar: ({ children, ...props }: any) => <div data-testid="sidebar" {...props}>{children}</div>,
  SidebarProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SidebarInset: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  SidebarHeader: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SidebarContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SidebarFooter: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SidebarGroup: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SidebarGroupLabel: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SidebarGroupContent: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SidebarMenu: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SidebarMenuButton: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SidebarMenuItem: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SidebarRail: () => null,
}))

jest.mock('@/context/auth-context', () => ({
  useAuth: jest.fn(() => ({
    isAuthenticated: true,
    token: 'fake-token',
    login: jest.fn(),
    logout: jest.fn(),
  })),
}))

jest.mock('@/components/custom-sidebar-trigger', () => {
  return function MockTrigger() {
    return <button aria-label="Open Menu">open</button>
  }
})

describe('NavSidebar (authenticated)', () => {
  it('renders Video Uploads link when logged in', () => {
    render(<NavSidebar />)
    expect(screen.getByText('Video Uploads')).toBeInTheDocument()
  })

  it('renders Logout button when logged in', () => {
    render(<NavSidebar />)
    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument()
  })

  it('does not render Login button when logged in', () => {
    render(<NavSidebar />)
    expect(screen.queryByRole('button', { name: /login/i })).not.toBeInTheDocument()
  })
})
