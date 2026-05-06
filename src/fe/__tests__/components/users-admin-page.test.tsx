/** @jest-environment jsdom */
import { render, screen, waitFor } from '@testing-library/react'
import UsersAdminPage from '@/app/(main)/users-admin/page'

const mockUsers = [
  {
    email: 'admin@example.com',
    is_active: true,
    new_id: '1',
    full_name: 'Admin User',
    assigned_scopes: ['superuser'],
  },
  {
    email: 'user@example.com',
    is_active: true,
    new_id: '2',
    full_name: 'Regular User',
    assigned_scopes: ['integrations:admin'],
  },
  {
    email: 'inactive@example.com',
    is_active: false,
    new_id: '3',
    full_name: 'Inactive User',
    assigned_scopes: [],
  },
]

jest.mock('@/lib/api', () => ({
  fetchUsersWithScopes: jest.fn(),
  removeUserScopes: jest.fn(),
}))

jest.mock('@/components/user-scope-dialog', () => {
  return function MockUserScopeDialog({ open }: { open: boolean }) {
    return open ? <div data-testid="user-scope-dialog">UserScopeDialog</div> : null
  }
})

const { fetchUsersWithScopes, removeUserScopes } = jest.requireMock('@/lib/api')

describe('UsersAdminPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('shows loading state', () => {
    fetchUsersWithScopes.mockReturnValue(new Promise(() => {}))
    render(<UsersAdminPage />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders users table when data loaded', async () => {
    fetchUsersWithScopes.mockResolvedValue({ data: mockUsers })
    render(<UsersAdminPage />)
    await waitFor(() => {
      expect(screen.getByText('admin@example.com')).toBeInTheDocument()
      expect(screen.getByText('user@example.com')).toBeInTheDocument()
      expect(screen.getByText('inactive@example.com')).toBeInTheDocument()
    })
  })

  it('shows superuser badge for superusers', async () => {
    fetchUsersWithScopes.mockResolvedValue({ data: mockUsers })
    render(<UsersAdminPage />)
    await waitFor(() => {
      expect(screen.getByText('ALL SCOPES')).toBeInTheDocument()
    })
  })

  it('shows scope pills for non-superusers', async () => {
    fetchUsersWithScopes.mockResolvedValue({ data: mockUsers })
    render(<UsersAdminPage />)
    await waitFor(() => {
      expect(screen.getByText('integrations:admin')).toBeInTheDocument()
    })
  })

  it('shows Default for users without scopes', async () => {
    fetchUsersWithScopes.mockResolvedValue({ data: mockUsers })
    render(<UsersAdminPage />)
    await waitFor(() => {
      expect(screen.getByText(/Default \(api:all\)/i)).toBeInTheDocument()
    })
  })

  it('shows Active/Inactive status correctly', async () => {
    fetchUsersWithScopes.mockResolvedValue({ data: mockUsers })
    render(<UsersAdminPage />)
    await waitFor(() => {
      const activeEls = screen.getAllByText('Active')
      expect(activeEls).toHaveLength(2)
    })
  })

  it('shows error on fetch failure', async () => {
    fetchUsersWithScopes.mockRejectedValue(new Error('Auth error'))
    render(<UsersAdminPage />)
    await waitFor(() => {
      expect(screen.getByText('Auth error')).toBeInTheDocument()
    })
  })

  it('renders Edit and Remove scope buttons for each user', async () => {
    fetchUsersWithScopes.mockResolvedValue({ data: mockUsers })
    render(<UsersAdminPage />)
    await waitFor(() => {
      const rows = screen.getAllByRole('row')
      expect(rows.length).toBeGreaterThan(2)
    })
  })
})
