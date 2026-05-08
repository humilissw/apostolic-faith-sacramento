/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen, fireEvent, act } from '@testing-library/react'
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
    isLoadingToken: false,
    login: jest.fn(),
    logout: jest.fn(),
    hasScope: jest.fn(() => false),
  })),
}))

jest.mock('@/components/custom-sidebar-trigger', () => {
  return function MockTrigger() {
    return <button aria-label="Open Menu">open</button>
  }
})

// Mock /auth/me to return non-superuser
global.fetch = jest.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ email: 'test@test.com', is_superuser: false }),
  }),
)

describe('NavSidebar (authenticated)', () => {
  beforeEach(() => {
    // Set auth cookie so the sidebar considers the user authenticated
    document.cookie = 'access_token=fake; path=/'
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ email: 'test@test.com', is_superuser: false }),
      }),
    )
  })

  it('renders Video Uploads link when logged in', async () => {
    await act(async () => {
      render(<NavSidebar />)
    })
    expect(screen.getByText('Video Uploads')).toBeInTheDocument()
  })

  it('renders Logout button when logged in', async () => {
    await act(async () => {
      render(<NavSidebar />)
    })
    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument()
  })

  it('does not render Login button when logged in', async () => {
    await act(async () => {
      render(<NavSidebar />)
    })
    expect(screen.queryByRole('button', { name: /login/i })).not.toBeInTheDocument()
  })

  it('does not render Integrations link for non-superuser', async () => {
    await act(async () => {
      render(<NavSidebar />)
    })
    expect(screen.queryByText('Integrations')).not.toBeInTheDocument()
  })
})
