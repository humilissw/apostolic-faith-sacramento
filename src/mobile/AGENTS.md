# Mobile AGENTS.md

## Project Overview

A React Native mobile app for the Apostolic Faith Sacramento church. Built on the Obytes React Native Template for production-ready development. Connects to the FastAPI backend for authentication and data.

**Architecture**: React Native + Expo Router (client-side) + FastAPI backend + Next.js frontend.

## Architecture

### Tech Stack

- **Framework**: Expo SDK 54 (React Native 0.81.5)
- **Router**: Expo Router 6 (file-based, like Next.js)
- **Language**: TypeScript 5.9+ (strict mode)
- **State**: Zustand (client state) + React Query (server state)
- **Forms**: TanStack Form + Zod 4
- **Storage**: MMKV (encrypted)
- **HTTP**: Axios
- **Styling**: NativeWind/Tailwind CSS v4 + tailwind-variants
- **Animations**: Moti + react-native-reanimated
- **Testing**: Jest + @testing-library/react-native
- **Lints**: ESLint (antfu) + commitlint
- **Build**: EAS (Expo Application Services)

### Project Structure

```
mobile/
├── src/
│   ├── app/                     # Expo Router file-based routes
│   │   ├── (app)/               # Authenticated route group
│   │   │   ├── _layout.tsx      # App layout (tabs/navigation)
│   │   │   ├── index.tsx        # Home screen
│   │   │   ├── feed.tsx         # Feed screen
│   │   │   ├── settings.tsx     # Settings screen
│   │   │   └── feed/            # Feed sub-routes
│   │   ├── login.tsx            # Login (public)
│   │   ├── onboarding.tsx       # Onboarding (public)
│   │   ├── _layout.tsx          # Root layout
│   │   └── +html.tsx            # Web fallback
│   ├── features/                # Feature modules
│   │   ├── auth/                # Auth feature
│   │   │   ├── login-screen.tsx
│   │   │   └── use-auth-store.tsx  # Zustand store
│   │   ├── feed/                # Feed feature
│   │   │   ├── feed-screen.tsx
│   │   │   ├── api.ts           # React Query hooks
│   │   │   └── components/
│   │   ├── settings/            # Settings feature
│   │   ├── home/                # Home feature
│   │   ├── onboarding/          # Onboarding feature
│   │   └── style-demo/          # Style demo
│   ├── components/
│   │   └── ui/                  # UI primitives (NativeWind)
│   │       ├── button.tsx
│   │       ├── input.tsx
│   │       ├── modal.tsx
│   │       ├── select.tsx
│   │       ├── checkbox.tsx
│   │       └── ...
│   ├── lib/                     # Shared utilities
│   │   ├── api/                 # Axios client + React Query provider
│   │   ├── auth/                # Token management (MMKV)
│   │   ├── hooks/               # Custom hooks
│   │   ├── i18n/                # i18next setup
│   │   ├── storage.tsx          # MMKV wrapper
│   │   └── utils.ts             # Helpers (createSelectors, cn)
│   ├── translations/            # i18n JSON files
│   └── global.css               # Tailwind config
├── __mocks__/                   # Jest mocks (native modules)
├── docs/                        # Mobile documentation site
├── cli/                         # Project setup CLI
├── app.config.ts                # Expo config
├── env.ts                       # Env var validation (Zod)
├── eas.json                     # EAS build profiles
├── jest.config.js               # Test config
├── package.json                 # Dependencies
└── tsconfig.json                # TypeScript config
```

## Development Patterns

### 1. Adding a New Feature

Create a folder in `src/features/[name]/` with the following structure:

```
src/features/[name]/
├── [name]-screen.tsx     # Main screen component
├── api.ts                 # React Query hooks (if API calls needed)
└── components/            # Feature-specific sub-components
```

**Example** — new "Prayer" feature:

```tsx
// src/features/prayer/prayer-screen.tsx
import { useState } from 'react'
import { View, Text } from 'react-native'
import { Button, Input } from '@/components/ui'

export function PrayerScreen() {
  const [text, setText] = useState('')
  return (
    <View className="p-4">
      <Input value={text} onChangeText={setText} placeholder="Enter prayer request" />
      <Button title="Submit" onPress={() => { /* submit */ }} />
    </View>
  )
}
```

### 2. Adding a New Route

Add a file in `src/app/` following Expo Router conventions:

```tsx
// src/app/prayers.tsx  — public route
export default function PrayersScreen() {
  return <PrayerScreen />
}

// src/app/(app)/prayers.tsx  — authenticated route (inside route group)
export default function PrayersScreen() {
  return <PrayerScreen />
}
```

### 3. API Calls (React Query)

```tsx
// src/features/prayer/api.ts
import { useQuery, useMutation } from '@tanstack/react-query'
import { useApi } from '@/lib/api'

export function usePrayerRequests() {
  const api = useApi()
  return useQuery({
    queryKey: ['prayers'],
    queryFn: async () => {
      const res = await api.get('/prayers')
      return res.data
    },
  })
}

export function useCreatePrayer() {
  const api = useApi()
  return useMutation({
    mutationFn: (data: { text: string }) => api.post('/prayers', data),
    onSuccess: () => {
      // Invalidate queries
    },
  })
}
```

### 4. Global State (Zustand)

```tsx
// src/features/prayer/use-prayer-store.tsx
import { create } from 'zustand'
import { createSelectors } from '@/lib/utils'

interface PrayerState {
  sortOrder: 'newest' | 'oldest'
  setSortOrder: (order: 'newest' | 'oldest') => void
}

const _usePrayerStore = create<PrayerState>((set) => ({
  sortOrder: 'newest',
  setSortOrder: (order) => set({ sortOrder: order }),
}))

export const usePrayerStore = createSelectors(_usePrayerStore)
```

### 5. UI Components

Use NativeWind (Tailwind) classes. For reusable components with variants, use `tailwind-variants`:

```tsx
import { cva, type VariantProps } from 'tailwind-variants'

const cardVariants = cva(
  'p-4 rounded-xl bg-white shadow-sm',
  {
    variants: {
      variant: {
        default: '',
        elevated: 'shadow-md',
        ghost: 'bg-transparent shadow-none',
      },
    },
    defaultVariants: { variant: 'default' },
  },
)

interface CardProps extends VariantProps<typeof cardVariants> {
  children: React.ReactNode
  className?: string
}

export function Card({ variant, className, children }: CardProps) {
  return <View className={`${cardVariants({ variant, className })}`}>{children}</View>
}
```

### 6. Authentication

Token management via MMKV:

```tsx
import { useAuthStore } from '@/features/auth/use-auth-store'

// Check auth
const token = useAuthStore((s) => s.token)
const isAuthenticated = !!token

// Sign out
const signOut = useAuthStore((s) => s.signOut)
signOut()
```

Token stored as `{ access: string; refresh: string }` in MMKV under key `token`.

### 7. API Interceptor (Auth Header)

Axios interceptor in `src/lib/api/provider.tsx` adds `Authorization: Bearer <token>` header when user is authenticated.

## Configuration

### Environment Variables

Defined in `.env` — validated by Zod schema in `env.ts`:

```
EXPO_PUBLIC_APP_ENV=development     # development | preview | production
EXPO_PUBLIC_API_URL=https://...     # Backend API URL
EXPO_PUBLIC_VAR_NUMBER=1
EXPO_PUBLIC_VAR_BOOL=true
```

### EAS Build

Profiles defined in `eas.json` — configured in `app.config.ts`:

| Profile | Purpose | Command |
|---------|---------|---------|
| development | Local dev | `eas build --profile development` |
| preview | Internal testing | `eas build --profile preview` |
| production | App store | `eas build --profile production` |

## Testing

```bash
# Run all tests
pnpm test

# CI with coverage
pnpm test:ci

# Watch mode
pnpm test:watch

# All quality checks
pnpm check-all
```

Test files co-located with components (`.test.tsx`). Jest uses `jest-expo` preset. Native module mocks in `__mocks__/`.

## Common Gotchas

### Native Modules
- Native modules need `pnpm prebuild` to generate `ios/` and `android/` directories
- Never edit generated native code directly — use `app.config.ts` plugins
- Dev client (`expo-dev-client`) required for native module hot reload

### Styling
- NativeWind converts Tailwind classes to RN style objects at build time
- Not all CSS properties work in React Native — check NativeWind docs
- Use `className` prop, not `style` for Tailwind classes
- `flex` and layout classes work well; complex layouts need `StyleSheet`

### Router
- File-based routing follows Expo Router conventions
- `(group)` folders are route groups (no URL impact)
- `[param]` folders create dynamic routes
- Layout screens wrap child screens — use `Slot` to render children
- Typed routes enabled (`typedRoutes: true` in app.config.ts)

### State
- Zustand stores persist in memory only — use MMKV for persistence
- React Query caches server state automatically
- Don't put API data in Zustand stores — use React Query instead
- Use `createSelectors()` helper for type-safe Zustand selectors

### Build
- `EXPO_PUBLIC_*` env vars are baked into the bundle at build time
- Changes to `app.config.ts` require restarting Expo
- Clear cache with `expo start -c` if env vars don't update
- New Arch is enabled — ensure native modules support it

## Resources

- [Expo Documentation](https://docs.expo.dev/)
- [Expo Router](https://docs.expo.dev/routing/)
- [Zustand](https://github.com/pmndrs/zustand)
- [React Query](https://tanstack.com/query)
- [NativeWind](https://www.nativewind.dev/)
- [Obytes Template](https://github.com/obytes/react-native-template-obytes)
- [CLAUDE.md](./CLAUDE.md) - Quick reference and patterns
