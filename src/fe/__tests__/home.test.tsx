/** @jest-environment jsdom */

import Home from '@/app/page'
import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'


describe('Page', () => {
  it('renders a heading', () => {
    render(<Home />)
 
    const heading = screen.getByText('APOSTOLIC FAITH CHURCH')
 
    expect(heading).toBeInTheDocument()
  })
})