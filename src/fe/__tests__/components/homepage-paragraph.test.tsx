/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import HomepageParagraph from '@/components/homepage-paragraph'

describe('HomepageParagraph', () => {
  it('renders the main description text', () => {
    render(<HomepageParagraph />)
    expect(screen.getByText(/part of a worldwide Christian organization/)).toBeInTheDocument()
  })

  it('renders text about Sacramento', () => {
    render(<HomepageParagraph />)
    expect(screen.getByText(/Sacramento/)).toBeInTheDocument()
  })

  it('matches snapshot', () => {
    const { container } = render(<HomepageParagraph />)
    expect(container).toMatchSnapshot()
  })
})
