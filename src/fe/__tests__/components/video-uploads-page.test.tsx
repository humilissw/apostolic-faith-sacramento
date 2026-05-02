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
  Sheet: ({ children, open, onOpenChange }: any) => (
    <div data-sheet-open={String(open)} data-on-open-change={String(onOpenChange)}>
      {children}
    </div>
  ),
  SheetTrigger: ({ asChild, children }: any) => <div data-sheet-trigger>{children}</div>,
  SheetContent: ({ children }: any) => <div data-sheet-content>{children}</div>,
  SheetHeader: ({ children }: any) => <div data-sheet-header>{children}</div>,
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

function renderPage() {
  const VideoUploadsPage = require('@/app/(main)/video-uploads/page').default
  return render(<VideoUploadsPage />)
}

describe('VideoUploadsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    jest.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('shows loading state initially', () => {
    global.fetch = jest.fn().mockReturnValue(
      new Promise(() => {}),
    )
    renderPage()
    expect(screen.getByText('Loading...')).toBeInTheDocument()
  })

  it('renders uploaded videos when data is available', async () => {
    global.fetch = jest.fn().mockReturnValue(
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ data: mockVideos, count: 1 }),
      }),
    )

    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Test Sermon')).toBeInTheDocument()
    })
  })

  it('renders the Upload a Video button', async () => {
    global.fetch = jest.fn().mockReturnValue(
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ data: [], count: 0 }),
      }),
    )

    renderPage()

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /upload a video/i })).toBeInTheDocument()
    })
  })

  it('opens the sheet when Upload a Video button is clicked', async () => {
    global.fetch = jest.fn().mockReturnValue(
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ data: [], count: 0 }),
      }),
    )

    renderPage()

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
    global.fetch = jest.fn().mockReturnValue(
      Promise.resolve({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      }),
    )

    renderPage()

    await waitFor(() => {
      expect(screen.getByText('Failed to load: 500')).toBeInTheDocument()
    })
  })

  it('shows empty state when no videos exist', async () => {
    global.fetch = jest.fn().mockReturnValue(
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ data: [], count: 0 }),
      }),
    )

    renderPage()

    await waitFor(() => {
      expect(screen.getByText('No videos uploaded yet.')).toBeInTheDocument()
    })
  })

  it('refreshes videos after upload success', async () => {
    let callCount = 0
    global.fetch = jest.fn().mockImplementation(() => {
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

    renderPage()

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
