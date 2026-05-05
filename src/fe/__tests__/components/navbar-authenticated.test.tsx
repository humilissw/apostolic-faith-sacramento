/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import Navbar from '@/components/navbar'

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn(() => ({
    matches: false,
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  })),
})

jest.mock('@/components/ui/sidebar', () => ({
  SidebarProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  SidebarInset: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  useSidebar: jest.fn(() => ({
    state: 'expanded',
    open: true,
    setOpen: jest.fn(),
    openMobile: true,
    setOpenMobile: jest.fn(),
    isMobile: false,
    toggleSidebar: jest.fn(),
  })),
}))

jest.mock('@/hooks/use-mobile', () => ({
  useIsMobile: jest.fn(() => false),
}))

global.fetch = jest.fn().mockResolvedValue({
  ok: true,
  json: () => Promise.resolve({ is_superuser: false }),
})

jest.mock('@/context/auth-context', () => ({
  useAuth: jest.fn(() => ({
    isAuthenticated: true,
    token: 'fake-token',
    login: jest.fn(),
    logout: jest.fn(),
  })),
}))

jest.mock('@/components/nav-sidebar', () => ({
  NavSidebar: () => <div data-testid="nav-sidebar">Nav Sidebar</div>,
}))

jest.mock('@/components/custom-sidebar-trigger', () => {
  return function MockTrigger() {
    return <button aria-label="Open Menu">open</button>
  }
})

describe('Navbar (authenticated)', () => {
  it('renders Video Uploads link when logged in', () => {
    const { container } = render(<Navbar />)
    const links = container.querySelectorAll('a')
    const videoLink = [...links].find((l) => l.textContent?.trim() === 'Video Uploads' && l.getAttribute('href')?.includes('video-uploads'))
    expect(videoLink).toBeInTheDocument()
  })

  it('renders a Logout button when logged in', () => {
    render(<Navbar />)
    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument()
  })

  it('does not render Login button when logged in', () => {
    render(<Navbar />)
    expect(screen.queryByRole('button', { name: /login/i })).not.toBeInTheDocument()
  })

  it('renders the AFC logo as a link', () => {
    render(<Navbar />)
    const logo = screen.getByAltText(/apostolic faith church/i)
    expect(logo).toBeInTheDocument()
    expect(logo.closest('a')).toHaveAttribute('href', '/')
  })

  it('renders Media link', () => {
    render(<Navbar />)
    expect(screen.getByText('Media')).toBeInTheDocument()
  })

  it('renders Contact Us link', () => {
    render(<Navbar />)
    expect(screen.getByText('Contact Us')).toBeInTheDocument()
  })

  it('renders Our Beliefs in About dropdown', () => {
    const { container } = render(<Navbar />)
    const triggers = container.querySelectorAll('[data-slot="navigation-menu-trigger"]')
    const aboutTrigger = [...triggers].find((t) => t.textContent?.includes('About'))
    expect(aboutTrigger).toBeInTheDocument()
  })

  it('renders Resources dropdown', () => {
    const { container } = render(<Navbar />)
    const triggers = container.querySelectorAll('[data-slot="navigation-menu-trigger"]')
    const resourcesTrigger = [...triggers].find((t) => t.textContent?.includes('Resources'))
    expect(resourcesTrigger).toBeInTheDocument()
  })
})
