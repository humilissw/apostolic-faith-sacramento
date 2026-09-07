/** @jest-environment jsdom */

import '@testing-library/jest-dom'
import { render, screen, waitFor } from '@testing-library/react'

import { FeatureFlagProvider, useFeatureFlags } from '@/context/feature-flag-context'
import { fetchWithAuth } from '@/lib/api/auth'

jest.mock('@/lib/api/auth', () => ({
  fetchWithAuth: jest.fn(),
}))

const mockedFetchWithAuth = fetchWithAuth as jest.MockedFunction<typeof fetchWithAuth>

function FlagsProbe() {
  const { flags, isLoading } = useFeatureFlags()
  if (isLoading) return <div>loading</div>
  return <div data-testid="flags">{JSON.stringify(flags)}</div>
}

describe('FeatureFlagProvider', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('fetches flags with cookie credentials via fetchWithAuth', async () => {
    mockedFetchWithAuth.mockResolvedValue(
      new Response(JSON.stringify({ data: [], count: 0 }), { status: 200 }),
    )

    render(
      <FeatureFlagProvider>
        <FlagsProbe />
      </FeatureFlagProvider>,
    )

    await waitFor(() => expect(screen.getByTestId('flags')).toBeInTheDocument())

    // Regression: the /feature-flags/ endpoint is superuser-only. The request
    // must go through fetchWithAuth (credentials: "include") — a bare fetch()
    // drops the session cookie cross-origin, so admins silently fell back to
    // DEFAULT_FLAGS and the navbar hid every admin link after login.
    expect(mockedFetchWithAuth).toHaveBeenCalledTimes(1)
    expect(mockedFetchWithAuth.mock.calls[0][0]).toContain('/feature-flags/')
  })

  it('applies server flags over defaults', async () => {
    mockedFetchWithAuth.mockResolvedValue(
      new Response(
        JSON.stringify({
          data: [
            { name: 'enable_users_admin', is_enabled: true },
            { name: 'enable_home', is_enabled: false },
          ],
          count: 2,
        }),
        { status: 200 },
      ),
    )

    render(
      <FeatureFlagProvider>
        <FlagsProbe />
      </FeatureFlagProvider>,
    )

    await waitFor(() => expect(screen.getByTestId('flags')).toBeInTheDocument())
    const flags = JSON.parse(screen.getByTestId('flags').textContent || '{}')
    expect(flags.enable_users_admin).toBe(true)
    expect(flags.enable_home).toBe(false)
  })

  it('keeps safe defaults when the endpoint rejects (unauthenticated)', async () => {
    mockedFetchWithAuth.mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Not authenticated' }), { status: 401 }),
    )

    render(
      <FeatureFlagProvider>
        <FlagsProbe />
      </FeatureFlagProvider>,
    )

    await waitFor(() => expect(screen.getByTestId('flags')).toBeInTheDocument())
    const flags = JSON.parse(screen.getByTestId('flags').textContent || '{}')
    // Public features stay usable, admin features stay hidden.
    expect(flags.enable_home).toBe(true)
    expect(flags.enable_users_admin).toBe(false)
  })
})
