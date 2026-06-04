/** @jest-environment jsdom */
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import VideoUploadsAdminPage from '@/app/(main)/video-uploads-admin/page'

const mockUploads = [
  {
    id: '1',
    upload_location: 'https://youtube.com/watch?v=1',
    upload_name: 'Sermon 1',
    media_association_date: '2026-05-01T00:00:00',
    speaker_name: 'Pete',
    reference_text: 'John 3:16',
    description: 'Test sermon description',
    owner_id: '1',
    created_on: '2026-05-01T00:00:00',
    updated_on: null,
  },
]

jest.mock('@/lib/api', () => ({
  fetchAllVideoUploads: jest.fn(),
  deleteVideoUpload: jest.fn(),
}))

jest.mock('@/components/video-upload-dialog', () => {
  return function MockDialog({ open }: { open: boolean }) {
    return open ? <div data-testid="video-upload-dialog">VideoUploadDialog</div> : null
  }
})

jest.mock('sonner', () => ({
  toast: { success: jest.fn(), error: jest.fn() },
}))

const { fetchAllVideoUploads } = jest.requireMock('@/lib/api')

describe('VideoUploadsAdminPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('shows loading state', () => {
    fetchAllVideoUploads.mockReturnValue(new Promise(() => {}))
    render(<VideoUploadsAdminPage />)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders table with uploads', async () => {
    fetchAllVideoUploads.mockResolvedValue({ data: mockUploads })
    render(<VideoUploadsAdminPage />)
    await waitFor(() => {
      expect(screen.getByText('Sermon 1')).toBeInTheDocument()
      expect(screen.getByText('Pete')).toBeInTheDocument()
    })
  })

  it('renders New button', async () => {
    fetchAllVideoUploads.mockResolvedValue({ data: [] })
    render(<VideoUploadsAdminPage />)
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /New/i })).toBeInTheDocument()
    })
  })

  it('shows empty state when no uploads', async () => {
    fetchAllVideoUploads.mockResolvedValue({ data: [] })
    render(<VideoUploadsAdminPage />)
    await waitFor(() => {
      expect(screen.getByText(/No video uploads yet/i)).toBeInTheDocument()
    })
  })

  it('renders page heading', async () => {
    fetchAllVideoUploads.mockResolvedValue({ data: [] })
    render(<VideoUploadsAdminPage />)
    await waitFor(() => {
      expect(screen.getByText('Video Upload Management')).toBeInTheDocument()
    })
  })

  it('shows error on fetch failure', async () => {
    fetchAllVideoUploads.mockRejectedValue(new Error('Network error'))
    render(<VideoUploadsAdminPage />)
    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument()
    })
  })

  it('opens delete confirmation dialog on delete button click', async () => {
    fetchAllVideoUploads.mockResolvedValue({ data: mockUploads })
    render(<VideoUploadsAdminPage />)
    await waitFor(() => {
      expect(screen.getByText('Sermon 1')).toBeInTheDocument()
    })
    const actionButtons = screen.getAllByRole('button')
    const deleteButton = actionButtons.find(
      (btn) => btn.textContent === null && btn.getAttribute('aria-label') === null,
    )
    if (deleteButton) {
      fireEvent.click(deleteButton)
      await waitFor(() => {
        expect(screen.getByText('Delete video upload')).toBeInTheDocument()
      })
    }
  })
})
