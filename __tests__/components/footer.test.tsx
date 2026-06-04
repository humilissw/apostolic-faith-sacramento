/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import Footer from '@/components/footer'

describe('Footer', () => {
  it('renders the church name', () => {
    render(<Footer />)
    expect(screen.getByText(/Apostolic Faith Church/)).toBeInTheDocument()
  })

  it('renders the current year copyright text', () => {
    render(<Footer />)
    const currentYear = new Date().getFullYear().toString()
    const text = screen.getByText(/202[0-9] Apostolic Faith Church/)
    expect(text).toHaveTextContent(currentYear)
  })

  it('renders a link to doctrines', () => {
    const { container } = render(<Footer />)
    const links = container.querySelectorAll('a')
    const doctrineLink = [...links].find((l) => l.textContent?.trim() === 'About')
    expect(doctrineLink).toHaveAttribute('href', '/doctrines')
  })

  it('renders a link to media', () => {
    const { container } = render(<Footer />)
    const links = container.querySelectorAll('a')
    const mediaLink = [...links].find((l) => l.textContent?.trim() === 'Media')
    expect(mediaLink).toHaveAttribute('href', '/media')
  })

  it('renders a link to contact', () => {
    const { container } = render(<Footer />)
    const links = container.querySelectorAll('a')
    const contactLink = [...links].find((l) => l.textContent?.trim() === 'Contact')
    expect(contactLink).toHaveAttribute('href', '/contact')
  })

  it('renders a link to the church email', () => {
    render(<Footer />)
    const link = screen.getByRole('link', { name: /info@afcsacramento\.org/i })
    expect(link).toHaveAttribute('href', 'mailto:info@afcsacramento.org')
  })

  it('renders a link to the church address', () => {
    render(<Footer />)
    const link = screen.getByRole('link', { name: /Elmont Ave/i })
    expect(link).toHaveAttribute('href', expect.stringContaining('google.com/maps'))
  })

  it('renders Contact Us section heading', () => {
    render(<Footer />)
    expect(screen.getByText('Contact Us')).toBeInTheDocument()
  })

  it('renders Quick Links heading', () => {
    render(<Footer />)
    expect(screen.getByText('Quick Links')).toBeInTheDocument()
  })

  it('renders the footer element', () => {
    const { container } = render(<Footer />)
    const footer = container.querySelector('footer')
    expect(footer).toBeInTheDocument()
  })
})
