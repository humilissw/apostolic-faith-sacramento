/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'

const mockOnSuccess = jest.fn()

jest.mock('@/context/auth-context', () => ({
  useAuth: jest.fn(() => ({
    isAuthenticated: true,
    token: 'test-token',
    login: jest.fn(),
    logout: jest.fn(),
  })),
}))

function renderForm() {
  const UploadForm = require('@/components/upload-form').default
  return render(<UploadForm onSuccess={mockOnSuccess} />)
}

describe('UploadForm', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockOnSuccess.mockClear()
    jest.spyOn(console, 'error').mockImplementation(() => {})
  })

  it('renders all form fields', () => {
    renderForm()
    expect(screen.getByLabelText(/video url/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/video title/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/service date/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/speaker/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/bible reference/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /upload/i })).toBeInTheDocument()
  })

  it('posts data on submit', async () => {
    global.fetch = jest.fn().mockReturnValue(
      Promise.resolve({
        ok: true,
        text: jest.fn().mockResolvedValue(''),
        json: jest.fn().mockResolvedValue({}),
      }),
    )

    renderForm()
    fireEvent.change(screen.getByLabelText(/video url/i), {
      target: { value: 'https://youtube.com/watch?v=test' },
    })
    fireEvent.change(screen.getByLabelText(/video title/i), {
      target: { value: 'Test Video' },
    })
    fireEvent.change(screen.getByLabelText(/service date/i), {
      target: { value: '2026-05-01' },
    })

    fireEvent.click(screen.getByRole('button', { name: /upload/i }))

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled()
      const [url, config] = (global.fetch as jest.Mock).mock.calls[0]
      expect(url).toContain('/api/v1/video-uploads/')
      expect(config.method).toBe('POST')
      expect(config.headers['Content-Type']).toContain('application/json')
    })
  })

  it('clears fields and calls onSuccess on success', async () => {
    global.fetch = jest.fn().mockReturnValue(
      Promise.resolve({
        ok: true,
        text: jest.fn().mockResolvedValue(''),
        json: jest.fn().mockResolvedValue({}),
      }),
    )

    renderForm()
    fireEvent.change(screen.getByLabelText(/video url/i), {
      target: { value: 'https://youtube.com/watch?v=test' },
    })
    fireEvent.change(screen.getByLabelText(/video title/i), {
      target: { value: 'Test Video' },
    })
    fireEvent.change(screen.getByLabelText(/service date/i), {
      target: { value: '2026-05-01' },
    })

    fireEvent.click(screen.getByRole('button', { name: /upload/i }))

    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalled()
    })
  })

  it('shows error message on failure', async () => {
    global.fetch = jest.fn().mockReturnValue(
      Promise.resolve({
        ok: false,
        text: jest.fn().mockResolvedValue('Upload failed'),
      }),
    )

    renderForm()
    fireEvent.change(screen.getByLabelText(/video url/i), {
      target: { value: 'https://youtube.com/watch?v=test' },
    })
    fireEvent.change(screen.getByLabelText(/video title/i), {
      target: { value: 'Test Video' },
    })
    fireEvent.change(screen.getByLabelText(/service date/i), {
      target: { value: '2026-05-01' },
    })

    fireEvent.click(screen.getByRole('button', { name: /upload/i }))

    await waitFor(() => {
      expect(screen.getByText('Upload failed')).toBeInTheDocument()
    })
  })

  it('disables the submit button while uploading', async () => {
    global.fetch = jest.fn().mockReturnValue(
      new Promise(() => {}),
    )

    renderForm()
    fireEvent.change(screen.getByLabelText(/video url/i), {
      target: { value: 'https://youtube.com/watch?v=test' },
    })
    fireEvent.change(screen.getByLabelText(/video title/i), {
      target: { value: 'Test Video' },
    })
    fireEvent.change(screen.getByLabelText(/service date/i), {
      target: { value: '2026-05-01' },
    })

    fireEvent.click(screen.getByRole('button', { name: /upload/i }))

    const uploadBtn = screen.getByRole('button', { name: /uploading/i })
    expect(uploadBtn).toBeDisabled()
  })
})
