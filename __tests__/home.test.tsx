/** @jest-environment jsdom */

import Home from '@/app/(main)/page'
import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'

jest.mock('@/context/feature-flag-context', () => ({
  useFeatureFlag: jest.fn(() => [true, undefined]),
}))


describe('Page', () => {
  it('renders a heading', () => {
    render(<Home />)

    const headings = screen.getAllByText(/APOSTOLIC FAITH/i)

    expect(headings.length).toBeGreaterThan(0)
  })
})
