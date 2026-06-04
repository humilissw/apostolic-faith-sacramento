/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'

const mockVideos = [
  {
    id: 'abc123',
    upload_location: 'https://youtube.com/watch?v=test',
    upload_name: 'Test Sermon',
    description: 'A test sermon',
    reference_text: 'John 3:16',
    speaker_name: 'Pastor Pete',
    media_association_date: '2026-05-01',
    created_on: '2026-05-01T00:00:00Z',
    updated_on: null,
    download_url: 'https://youtube.com/watch?v=test',
  },
]

jest.mock('@/components/ui/sheet', () => ({
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  Sheet: ({ children, open, onOpenChange }: any) => (
    <div data-sheet-open={String(open)} data-on-open-change={String(onOpenChange)}>
      {children}
    </div>
  ),
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  SheetTrigger: ({ children }: any) => <div data-sheet-trigger>{children}</div>,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  SheetContent: ({ children }: any) => <div data-sheet-content>{children}</div>,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  SheetHeader: ({ children }: any) => <div data-sheet-header>{children}</div>,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  SheetTitle: ({ children }: any) => <div data-testid="sheet-title">{children}</div>,
}))

jest.mock('@/components/upload-form', () => {
  return function MockUploadForm({ onSuccess }: { onSuccess: () => void }) {
    return (
      <div data-testid="upload-form">
        <span>Upload Form</span>
        <button data-testid="upload-submit" onClick={onSuccess}>
          Submit
        </button>
      </div>
    )
  }
})

jest.mock('@/lib/api', () => ({
  fetchWithAuth: jest.fn(),
}))

jest.unmock('@/app/(main)/video-uploads/page')

function renderPage(mockFn?: jest.Mock) {
  if (mockFn) {
    const api = jest.requireMock('@/lib/api')
    ;(api.fetchWithAuth as jest.Mock).mockImplementation(mockFn)
  }
  const VideoUploadsPage = jest.requireActual('@/app/(main)/video-uploads/page').default
  return render(<VideoUploadsPage />)
}

describe('VideoUploadsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    jest.spyOn(console, 'error').mockImplementation(() => {})
  })

  function mockVideosResponse(videos: typeof mockVideos) {
    return async () => ({
      ok: true,
      json: () => Promise.resolve({ data: videos, count: videos.length }),
    })
  }

  it('shows loading state initially', () => {
    renderPage(() => new Promise(() => {}))
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders uploaded videos when data is available', async () => {
    renderPage(mockVideosResponse(mockVideos))
    await waitFor(() => {
      expect(screen.getByText('Test Sermon')).toBeInTheDocument()
    })
  })

  it('renders the Upload a Video button', async () => {
    renderPage(mockVideosResponse([]))
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /upload a video/i })).toBeInTheDocument()
    })
  })

  it('opens the sheet when Upload a Video button is clicked', async () => {
    renderPage(mockVideosResponse([]))
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /upload a video/i })).toBeInTheDocument()
    })
    const uploadBtn = screen.getByRole('button', { name: /upload a video/i })
    fireEvent.click(uploadBtn)
    await waitFor(() => {
      expect(screen.getByTestId('sheet-title')).toBeInTheDocument()
    })
  })

  it('shows error when fetch fails', async () => {
    renderPage(() => Promise.reject(new Error('Connection refused')))
    await waitFor(() => {
      expect(screen.getByText('Connection refused')).toBeInTheDocument()
    })
  })

  it('shows empty state when no videos exist', async () => {
    renderPage(mockVideosResponse([]))
    await waitFor(() => {
      expect(screen.getByText('No videos uploaded yet.')).toBeInTheDocument()
    })
  })

  it('refreshes videos after upload success', async () => {
    let callCount = 0
    const mockFn = jest.fn().mockImplementation(() => {
      callCount++
      if (callCount === 1) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ data: [], count: 0 }),
        })
      }
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ data: mockVideos, count: 1 }),
      })
    })
    renderPage(mockFn)
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /upload a video/i })).toBeInTheDocument()
    })
    const sheetBtn = screen.getByRole('button', { name: /upload a video/i })
    fireEvent.click(sheetBtn)
    await waitFor(() => {
      expect(screen.getByTestId('sheet-title')).toBeInTheDocument()
    })
    const uploadForm = screen.getByTestId('upload-form')
    fireEvent.click(uploadForm.querySelector('[data-testid="upload-submit"]')!)
    await waitFor(() => {
      expect(screen.getByText('Test Sermon')).toBeInTheDocument()
    })
  })
})
