/** @jest-environment jsdom */
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import UploadVideosPage from '@/app/(media)/upload-videos/page'

jest.mock('@/lib/api', () => ({
  fetchWithAuth: jest.fn(),
}))

const { fetchWithAuth } = jest.requireMock('@/lib/api')

describe('UploadVideosPage', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders the page heading', () => {
    fetchWithAuth.mockResolvedValue({ ok: true })
    render(<UploadVideosPage />)
    expect(screen.getByText('Upload a Video')).toBeInTheDocument()
  })

  it('renders all form fields', () => {
    fetchWithAuth.mockResolvedValue({ ok: true })
    render(<UploadVideosPage />)
    expect(screen.getByLabelText(/Video URL/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Video Title/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Service Date/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Speaker/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Bible Reference/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/Description/i)).toBeInTheDocument()
  })

  it('submits the form successfully', async () => {
    fetchWithAuth.mockResolvedValue({ ok: true, json: async () => ({}) })
    render(<UploadVideosPage />)
    fireEvent.change(screen.getByLabelText(/Video URL/i), {
      target: { value: 'https://youtube.com/watch?v=test' },
    })
    fireEvent.change(screen.getByLabelText(/Video Title/i), {
      target: { value: 'Test Video' },
    })
    fireEvent.change(screen.getByLabelText(/Service Date/i), {
      target: { value: '2026-05-01' },
    })
    fireEvent.click(screen.getByRole('button', { name: /Upload Video/i }))
    await waitFor(() => {
      expect(screen.getByText('Video uploaded successfully!')).toBeInTheDocument()
    })
  })

  it('shows upload state while submitting', async () => {
    fetchWithAuth.mockImplementation(() => new Promise(() => {}))
    render(<UploadVideosPage />)
    fireEvent.change(screen.getByLabelText(/Video URL/i), {
      target: { value: 'https://youtube.com/watch?v=test' },
    })
    fireEvent.change(screen.getByLabelText(/Video Title/i), {
      target: { value: 'Test Video' },
    })
    fireEvent.change(screen.getByLabelText(/Service Date/i), {
      target: { value: '2026-05-01' },
    })
    fireEvent.click(screen.getByRole('button', { name: /Upload Video/i }))
    await waitFor(() => {
      expect(screen.getByText('Uploading...')).toBeInTheDocument()
    })
  })

  it('shows error message on failed submission', async () => {
    fetchWithAuth.mockResolvedValue({ ok: false, text: async () => 'Error' })
    render(<UploadVideosPage />)
    fireEvent.change(screen.getByLabelText(/Video URL/i), {
      target: { value: 'https://youtube.com/watch?v=test' },
    })
    fireEvent.change(screen.getByLabelText(/Video Title/i), {
      target: { value: 'Test Video' },
    })
    fireEvent.change(screen.getByLabelText(/Service Date/i), {
      target: { value: '2026-05-01' },
    })
    fireEvent.click(screen.getByRole('button', { name: /Upload Video/i }))
    await waitFor(() => {
      expect(screen.getByText(/Error/i)).toBeInTheDocument()
    })
  })

  it('disables submit button while uploading', async () => {
    fetchWithAuth.mockImplementation(() => new Promise(() => {}))
    render(<UploadVideosPage />)
    fireEvent.change(screen.getByLabelText(/Video URL/i), {
      target: { value: 'https://youtube.com/watch?v=test' },
    })
    fireEvent.change(screen.getByLabelText(/Video Title/i), {
      target: { value: 'Test Video' },
    })
    fireEvent.change(screen.getByLabelText(/Service Date/i), {
      target: { value: '2026-05-01' },
    })
    fireEvent.click(screen.getByRole('button', { name: /Upload Video/i }))
    await waitFor(() => {
      const button = screen.getByRole('button', { name: /Uploading\.\.\./i })
      expect(button).toBeDisabled()
    })
  })
})
