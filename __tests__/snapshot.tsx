import Home from '@/app/(main)/page'
import { render } from '@testing-library/react'

jest.mock('@/context/feature-flag-context', () => ({
  useFeatureFlag: jest.fn(() => true),
}))

it('renders homepage unchanged', () => {
  const { container } = render(<Home />)
  expect(container).toMatchSnapshot()
})
