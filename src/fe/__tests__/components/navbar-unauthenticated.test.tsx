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

jest.mock('@/context/auth-context', () => ({
  useAuth: jest.fn(() => ({
    isAuthenticated: false,
    token: null,
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

describe('Navbar (unauthenticated)', () => {
  it('renders the AFC logo as a link', () => {
    render(<Navbar />)
    const logo = screen.getByAltText(/apostolic faith church/i)
    expect(logo).toBeInTheDocument()
    expect(logo.closest('a')).toHaveAttribute('href', '/')
  })

  it('renders a Login button', () => {
    render(<Navbar />)
    const loginBtn = screen.getByRole('button', { name: /login/i })
    expect(loginBtn).toBeInTheDocument()
  })

  it('links the Login button to /login/', () => {
    const { container } = render(<Navbar />)
    const links = container.querySelectorAll('a')
    const loginLink = [...links].find((l) => l.textContent?.trim() === 'Login')
    expect(loginLink).toHaveAttribute('href', '/login')
  })

  it('renders Media link', () => {
    const { container } = render(<Navbar />)
    const links = container.querySelectorAll('a')
    const mediaLink = [...links].find((l) => l.textContent?.trim() === 'Media')
    expect(mediaLink).toHaveAttribute('href', '/media')
  })

  it('renders Contact Us link', () => {
    const { container } = render(<Navbar />)
    const links = container.querySelectorAll('a')
    const contactLink = [...links].find((l) => l.textContent?.trim() === 'Contact Us')
    expect(contactLink).toHaveAttribute('href', '/contact')
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

  it('does not render Video Uploads when not logged in', () => {
    render(<Navbar />)
    expect(screen.queryByText('Video Uploads')).not.toBeInTheDocument()
  })
})
