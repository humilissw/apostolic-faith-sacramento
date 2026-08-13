# Expo SDK 56 - Developer Reference

## Core Docs

- **All SDK packages**: https://docs.expo.dev/versions/v56.0.0/
- **Router**: https://docs.expo.dev/versions/v56.0.0/router/
- **Theming**: https://docs.expo.dev/develop/user-interface/color-themes/
- **App icons**: https://docs.expo.dev/versions/v56.0.0/guides/app-icons/
- **Splash screen**: https://docs.expo.dev/versions/v56.0.0/api/splash-screen/
- **Animations**: https://docs.expo.dev/versions/v56.0.0/reanimated/

## Expo Router Rules

- Files in `src/app/` auto-map to routes
- `_layout.tsx` wraps child routes (never delete/renamed without understanding)
- Route groups use `(folder)/` prefix
- Dynamic routes use `[param]` or `[...slug]`
- Layout files persist across route changes (state is preserved)
- Use `usePathname()`, `useSearchParams()` for navigation state
- External URLs must use `ExternalLink` component (handles in-app browser on native)

## Component Conventions

### ThemedText
```tsx
<ThemedText type="title">Hello</ThemedText>
<ThemedText type="small">Body text</ThemedText>
<ThemedText themeColor="textSecondary">Secondary</ThemedText>
```

### ThemedView
```tsx
<ThemedView type="backgroundElement">Card</ThemedView>
<ThemedView style={{ marginTop: Spacing.two }}>Padded</ThemedView>
```

### Spacing Scale
```
Spacing.half  = 2
Spacing.one   = 4
Spacing.two   = 8
Spacing.three = 16
Spacing.four  = 24
Spacing.five  = 32
Spacing.six   = 64
```

## Adding a New Screen

1. Create `src/app/[name].tsx`
2. If it needs shared layout, add `src/app/[name]/_layout.tsx`
3. Import from `expo-router` for navigation: `router.push('/route')`
4. Use `ThemedText`/`ThemedView` for consistent styling
5. Use `useTheme()` for dynamic colors

## Adding a New Component

1. Create in `src/components/`
2. If platform-specific, add `[name].web.tsx` or `[name].native.tsx`
3. Export named (not default) for tree-shaking
4. Use `@/` path alias: `import { Foo } from '@/components/foo'`

## Adding a Native Module

1. `npx expo install [package-name]` (pins correct SDK version)
2. For iOS: `npx expo prebuild` to regenerate native project
3. For Android: same `npx expo prebuild`
4. Check https://docs.expo.dev/versions/v56.0.0/ for API docs

## Colors

```ts
Colors.light  = { text: '#000', background: '#fff', backgroundElement: '#F0F0F3', ... }
Colors.dark   = { text: '#fff', background: '#000', backgroundElement: '#212225', ... }
```

Use `theme.text`, `theme.background`, `theme.backgroundElement`, `theme.textSecondary`.
Primary link color: `#3c87f7` (hardcoded in ThemedText.linkPrimary).

## App Configuration (app.json)

- `expo-router` plugin enables file-based routing
- `expo-splash-screen` plugin configures splash (background `#208AEF`)
- `typedRoutes: true` = route types auto-generated
- `reactCompiler: true` = React Compiler transforms code
- `scheme: "afcmobile"` = deep link scheme (`afcmobile://`)

## Common Gotchas

- `npx expo install` not `pnpm add` for native modules (SDK version pinning)
- `require()` for static images only (not dynamic paths)
- `expo-image` for dynamic images, `require()` for static
- Reanimated needs `unstable_settings` in layout for hooks like `useReanimatedScrollProps`
- Web builds may differ from native - test on all platforms
