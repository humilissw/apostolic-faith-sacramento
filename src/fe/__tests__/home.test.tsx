/** @jest-environment jsdom */

import Home from '@/app/(main)/page'
import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'

jest.mock('@/context/feature-flag-context', () => ({
  useFeatureFlag: jest.fn(() => true),
}))


describe('Page', () => {
  it('renders a heading', () => {
    render(<Home />)

    const heading = screen.getByText('APOSTOLIC FAITH CHURCH')

    expect(heading).toBeInTheDocument()
  })
})
