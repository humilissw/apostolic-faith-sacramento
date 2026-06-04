/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { SearchForm } from '@/components/search-form'

describe('SearchForm', () => {
  it('renders a form element', () => {
    const { container } = render(<SearchForm />)
    const form = container.querySelector('form')
    expect(form).toBeInTheDocument()
  })

  it('renders a search input', () => {
    render(<SearchForm />)
    const input = screen.getByLabelText('Search')
    expect(input).toBeInTheDocument()
  })

  it('passes form props through', () => {
    const { container } = render(<SearchForm className="custom-class" />)
    const form = container.querySelector('form')
    expect(form).toHaveClass('custom-class')
  })
})
