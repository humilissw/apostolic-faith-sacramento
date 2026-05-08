/** @jest-environment jsdom */
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import UsersAdminPage from '@/app/(main)/users-admin/page'

// Polyfill ResizeObserver for jsdom
Object.defineProperty(window, 'ResizeObserver', {
  writable: true,
  value: class MockResizeObserver {
    observe = jest.fn()
    disconnect = jest.fn()
  },
})

const DEFAULT_MOCK_USERS = [
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

jest.mock('@/lib/api', () => {
  const mockFetchUsers = jest.fn().mockResolvedValue({
    data: [
      { email: 'admin@example.com', is_active: true, new_id: '1', full_name: 'Admin User', assigned_scopes: ['superuser'] },
      { email: 'user@example.com', is_active: true, new_id: '2', full_name: 'Regular User', assigned_scopes: ['integrations:admin'] },
      { email: 'inactive@example.com', is_active: false, new_id: '3', full_name: 'Inactive User', assigned_scopes: [] },
    ],
    count: 3,
  })
  const mockDeleteUser = jest.fn()
  const mockDeleteUsers = jest.fn()
  return {
    fetchUsersWithScopes: mockFetchUsers,
    deleteUser: mockDeleteUser,
    deleteUsers: mockDeleteUsers,
  }
})

jest.mock('@/components/user-scope-dialog', () => {
  return function MockUserScopeDialog({ open }: { open: boolean }) {
    return open ? <div data-testid="user-scope-dialog">UserScopeDialog</div> : null
  }
})


// Access mocks after module is loaded
const { fetchUsersWithScopes, deleteUser, deleteUsers } = require('@/lib/api')

describe('UsersAdminPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    window.confirm = jest.fn(() => true)
  })

  it('shows loading state', () => {
    fetchUsersWithScopes.mockReturnValueOnce(new Promise(() => {}))
    render(<UsersAdminPage />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders users table when data loaded', async () => {
    render(<UsersAdminPage />)
    await waitFor(() => {
      expect(screen.getByText('admin@example.com')).toBeInTheDocument()
      expect(screen.getByText('user@example.com')).toBeInTheDocument()
      expect(screen.getByText('inactive@example.com')).toBeInTheDocument()
    })
  })

  it('shows superuser badge for superusers', async () => {
    render(<UsersAdminPage />)
    await waitFor(() => {
      expect(screen.getByText('ALL SCOPES')).toBeInTheDocument()
    })
  })

  it('shows scope pills for non-superusers', async () => {
    render(<UsersAdminPage />)
    await waitFor(() => {
      expect(screen.getByText('integrations:admin')).toBeInTheDocument()
    })
  })

  it('shows Default for users without scopes', async () => {
    render(<UsersAdminPage />)
    await waitFor(() => {
      expect(screen.getByText(/Default \(api:all\)/i)).toBeInTheDocument()
    })
  })

  it('shows Active/Inactive status correctly', async () => {
    render(<UsersAdminPage />)
    await waitFor(() => {
      const activeEls = screen.getAllByText('Active')
      expect(activeEls).toHaveLength(2)
    })
  })


  it('renders Edit and Remove scope buttons for each user', async () => {
    render(<UsersAdminPage />)
    await waitFor(() => {
      const rows = screen.getAllByRole('row')
      expect(rows.length).toBeGreaterThan(2)
    })
  })

  it('shows select-all checkbox in table header', async () => {
    render(<UsersAdminPage />)
    await waitFor(() => {
      const checkboxes = screen.getAllByRole('checkbox')
      expect(checkboxes.length).toBeGreaterThan(1)
    })
  })

  it('shows bulk delete button when users are selected', async () => {
    render(<UsersAdminPage />)
    await waitFor(() => {
      const checkboxes = screen.getAllByRole('checkbox')
      fireEvent.click(checkboxes[0]) // select-all
    })
    expect(screen.getByText(/Delete selected/i)).toBeInTheDocument()
  })

  it('clears selection after bulk delete', async () => {
    deleteUsers.mockResolvedValueOnce(undefined)
    render(<UsersAdminPage />)
    await waitFor(() => {
      const checkboxes = screen.getAllByRole('checkbox')
      fireEvent.click(checkboxes[0]) // select-all
    })
    await waitFor(() => {
      const bulkBtn = screen.getByText(/Delete selected/i)
      fireEvent.click(bulkBtn)
    })
    await waitFor(() => {
      expect(deleteUsers).toHaveBeenCalled()
    })
  })

  it('shows load-more indicator when more users available', async () => {
    fetchUsersWithScopes.mockResolvedValueOnce({ data: DEFAULT_MOCK_USERS, count: 150 })
    render(<UsersAdminPage />)
    await waitFor(() => {
      expect(screen.getByText(/Displaying 3 of 150 Users/i)).toBeInTheDocument()
    })
  })

  it('hides load-more when all users loaded', async () => {
    fetchUsersWithScopes.mockResolvedValueOnce({ data: DEFAULT_MOCK_USERS, count: 3 })
    render(<UsersAdminPage />)
    await waitFor(() => {
      expect(screen.getByText(/Displaying 3 of 3 Users/i)).toBeInTheDocument()
    })
  })

  it('hides load-more when all users loaded', async () => {
    fetchUsersWithScopes.mockResolvedValueOnce({ data: DEFAULT_MOCK_USERS, count: 3 })
    render(<UsersAdminPage />)
    await waitFor(() => {
      expect(screen.getByText(/Displaying 3 of 3 Users/i)).toBeInTheDocument()
    })
  })
})
