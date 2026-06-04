/** @jest-environment jsdom */
import { render, screen } from '@testing-library/react'
import LiveServicePage from '@/app/(main)/live-service/page'

describe('LiveServicePage', () => {
  it('renders the Google Maps iframe', () => {
    render(<LiveServicePage />)
    const iframe = screen.getByTitle('Apostolic Faith Church Location')
    expect(iframe).toBeInTheDocument()
    expect(iframe).toHaveAttribute('src', expect.stringContaining('google.com/maps'))
  })

  it('renders the church address', () => {
    render(<LiveServicePage />)
    expect(screen.getByText(/Elmont Ave/i)).toBeInTheDocument()
  })

  it('renders the mailing address', () => {
    render(<LiveServicePage />)
    expect(screen.getByText(/Wortell Drive/i)).toBeInTheDocument()
  })

  it('renders email labels', () => {
    render(<LiveServicePage />)
    expect(screen.getByText(/Pastor:/i)).toBeInTheDocument()
    expect(screen.getByText(/Media Team:/i)).toBeInTheDocument()
  })

  it('has clickable email links', () => {
    render(<LiveServicePage />)
    const mailtoLinks = screen.getAllByRole('link')
    const emailLinks = mailtoLinks.filter((link) =>
      link.getAttribute('href')?.startsWith('mailto:'),
    )
    expect(emailLinks).toHaveLength(2)
  })
})
