/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render } from '@testing-library/react'
import SermonVideos from '@/components/sermon-videos'

Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn(() => ({
    matches: false,
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
  })),
})

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useSearchParams: () => ({
    get: (key: string) => {
      const params: Record<string, string> = {
        uri: 'https://www.youtube.com/embed/test-video',
        sermonTitle: 'Test Sermon',
        speaker: 'Pastor Pete',
        date: '2026-04-30',
      }
      return params[key]
    },
  }),
}))

describe('SermonVideos', () => {
  it('renders an iframe', () => {
    const { container } = render(<SermonVideos />)
    const iframe = container.querySelector('iframe')
    expect(iframe).toBeInTheDocument()
  })

  it('sets the iframe src from search params', () => {
    const { container } = render(<SermonVideos />)
    const iframe = container.querySelector('iframe')
    expect(iframe).toHaveAttribute('src', 'https://www.youtube.com/embed/test-video')
  })

  it('sets the iframe title from search params', () => {
    const { container } = render(<SermonVideos />)
    const iframes = container.querySelectorAll('iframe')
    // All iframes should have the same title
    iframes.forEach((iframe) => {
      expect(iframe).toHaveAttribute('title', 'Test Sermon')
    })
  })

  it('renders multiple iframes at different breakpoints', () => {
    const { container } = render(<SermonVideos />)
    const iframes = container.querySelectorAll('iframe')
    expect(iframes.length).toBeGreaterThan(1)
  })
})
