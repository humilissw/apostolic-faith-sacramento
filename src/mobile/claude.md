# Mobile CLAUDE.md

## Project Overview

React Native mobile app for the Apostolic Faith Sacramento church. Built on Obytes template. Uses Expo SDK 54, Expo Router 6, Zustand state, React Query data fetching.

## Quick Start

```bash
# Setup
pnpm install

# Run locally
pnpm start              # Expo dev server
pnpm ios                # iOS simulator
pnpm android            # Android emulator

# Build & test
pnpm lint               # ESLint check
pnpm type-check         # TypeScript validation
pnpm test               # Jest tests
pnpm check-all          # All quality checks

# Production builds
pnpm build:production:ios    # EAS iOS build
pnpm build:production:android # EAS Android build
```

## Key Files

- `app.config.ts` - Expo configuration (bundle ID, scheme, plugins)
- `env.ts` - Environment variable validation (Zod schema)
- `src/app/` - Expo Router routes (file-based routing)
- `src/features/` - Feature modules
- `src/lib/api/client.tsx` - Axios HTTP client (baseURL from env)
- `src/lib/auth/utils.tsx` - Token storage (MMKV)
- `src/lib/auth/use-auth-store.tsx` - Auth state (Zustand)
- `src/lib/storage.tsx` - MMKV storage wrapper
- `src/components/ui/` - UI primitives (button, input, modal, select, etc.)
- `jest.config.js` + `jest-setup.ts` - Test config
- `eas.json` - EAS build profiles

## Architecture Patterns

### App Router (Expo Router)

```
src/app/
├── _layout.tsx          # Root layout
├── +html.tsx            # Web fallback
├── (app)/               # Authenticated route group
│   ├── _layout.tsx      # App layout (tabs/nav)
│   ├── index.tsx        # Home screen
│   ├── feed.tsx         # Feed screen
│   ├── settings.tsx     # Settings screen
│   ├── style.tsx        # Style demo
│   └── feed/
│       ├── [id].tsx     # Post detail
│       └── add-post.tsx # Add post
├── login.tsx            # Login screen
└── onboarding.tsx       # Onboarding screen
```

### Feature Structure

```
src/features/[name]/
├── [name]-screen.tsx     # Main screen
├── api.ts                 # React Query hooks
├── components/            # Feature-specific components
└── use-[name]-store.tsx   # Zustand store (if needed)
```

### State Management

**Zustand** for client state (auth, preferences):

```tsx
import { create } from 'zustand'
import { createSelectors } from '@/lib/utils'

const _useStore = create((set) => ({
  token: null,
  signIn: (token) => set({ token }),
  signOut: () => set({ token: null }),
}))

export const useAuthStore = createSelectors(_useStore)
```

**React Query** for server state (API data):

```tsx
import { useQuery } from '@tanstack/react-query'
import { useApi } from '@/lib/api'

export function useFeed() {
  const api = useApi()
  return useQuery({
    queryKey: ['feed'],
    queryFn: () => api.get('/feed'),
  })
}
```

### UI Component Pattern

```tsx
import { cva, type VariantProps } from 'tailwind-variants'
import { Text } from 'react-native'

const buttonVariants = cva(
  'px-4 py-2 rounded-lg',
  {
    variants: {
      variant: {
        primary: 'bg-primary',
        secondary: 'bg-muted',
      },
    },
    defaultVariants: { variant: 'primary' },
  },
)

interface ButtonProps extends VariantProps<typeof buttonVariants> {
  title: string
}

export function Button({ variant, title }: ButtonProps) {
  return <Text className={buttonVariants({ variant })}>{title}</Text>
}
```

### Authentication Flow

1. **Login screen** (`src/app/login.tsx`) collects credentials
2. Calls API via `@/lib/api/client` (Axios instance)
3. On success: `useAuthStore.signIn({ access, refresh })` writes to MMKV
4. `hydrate()` on app start restores token from storage
5. Auth guards check `useAuthStore().token` before rendering protected routes

### API Client

```tsx
import axios from 'axios'
import Env from 'env'

export const client = axios.create({
  baseURL: Env.EXPO_PUBLIC_API_URL,
})

// Add auth header interceptor in provider
```

## Configuration

### Environment Variables

Validated by Zod schema in `env.ts`. Required vars:

```
EXPO_PUBLIC_APP_ENV=development    # development | preview | production
EXPO_PUBLIC_API_URL=https://...    # Backend API URL
EXPO_PUBLIC_NAME=ObytesApp
EXPO_PUBLIC_BUNDLE_ID=com.obytes.development
EXPO_PUBLIC_SCHEME=obytesApp
```

Environments: `development`, `preview`, `production`. Each has different bundle IDs and schemes.

### EAS Build Profiles

Configured in `eas.json` and `app.config.ts`:

- **development** - local dev build
- **preview** - internal testing
- **production** - app store build

## Development

- **React Native** 0.81.5 + **Expo SDK 54**
- **Expo Router 6** (file-based routing)
- **TypeScript** 5.9+ (strict)
- **TailwindCSS** via NativeWind/Uniwind
- **Zustand** for global state
- **React Query** for server state
- **TanStack Form + Zod** for forms
- **MMKV** for encrypted local storage
- **Jest + RTL** for testing

## Gotchas

1. Use `@/` imports, never relative imports from `src/`
2. Never modify `ios/` or `android/` directly — use `app.config.ts` plugins
3. Env vars validated by Zod at startup — missing vars break prebuild
4. New Arch enabled (`newArchEnabled: true`)
5. Expo Dev Client required for native modules in dev
6. Screens in `(app)/` route group are authenticated — screens outside are public
7. Jest uses `jest-expo` preset — polyfills native modules via `__mocks__/`

## Resources

- [Expo Documentation](https://docs.expo.dev/)
- [Expo Router](https://docs.expo.dev/routing/)
- [AGENTS.md](./AGENTS.md) - Detailed patterns and conventions
