/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import AFCLogo from '@/components/afc-logo'

describe('AFCLogo', () => {
  it('renders the logo image with the correct alt text', () => {
    render(<AFCLogo width={125} height={125} />)
    const img = screen.getByAltText('Apostolic Faith Church Logo')
    expect(img).toBeInTheDocument()
  })

  it('renders as a link', () => {
    render(<AFCLogo width={125} height={125} />)
    const link = screen.getByRole('link')
    expect(link).toBeInTheDocument()
    expect(link).toHaveAttribute('href', '/')
  })

  it('passes width and height props to the image', () => {
    render(<AFCLogo width={200} height={300} />)
    const img = screen.getByAltText('Apostolic Faith Church Logo')
    expect(img).toHaveAttribute('width', '200')
    expect(img).toHaveAttribute('height', '300')
  })

  it('matches snapshot', () => {
    const { container } = render(<AFCLogo width={120} height={145} />)
    expect(container).toMatchSnapshot()
  })
})
