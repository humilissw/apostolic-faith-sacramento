# AFC Mobile - CLAUDE.md

## Project Overview

Expo SDK 56 app for Apostolic Faith Sacramento church. Part of a tri-platform app:
- **Backend**: FastAPI (Python) at `/src/be/`
- **Frontend**: React at `/src/fe/`
- **Mobile**: Expo Router (React Native) - this directory

## Architecture

### Framework
- **Expo SDK 56** with Expo Router file-based routing
- React 19, React Native 0.85, TypeScript 6
- React Compiler enabled (`experiments.reactCompiler: true`)
- Typed routes enabled (`experiments.typedRoutes: true`)

### Routing
- File-based routing in `src/app/` directory
- **Drawer navigation** as the primary layout (hamburger menu)
- `_layout.tsx` = root layout with `ThemeProvider` + `Drawer` via `withLayoutContext`
- `index.tsx` = home screen with tab bar (tappable to switch tabs) + hamburger button
- `explore.tsx` = explore/info screen
- Drawer screens: `sermons.tsx`, `doctrines.tsx`, `media.tsx`, `live-service.tsx`, `donate.tsx`, `contact.tsx`
- Drawer configured via `withLayoutContext(createDrawerNavigator().Navigator)` from `expo-router`
- Navigation: `useNavigation()` hook -> `(navigation as any).openDrawer()` for drawer toggle
- Web fallback: `app-tabs.web.tsx` renders on web (standard tab bar)

### Key Patterns
- **Theming**: `useTheme()` hook returns current Colors map (light/dark). `useColorScheme()` from react-native for raw scheme.
- **Typography**: `ThemedText` with `type` prop (`default|title|small|smallBold|subtitle|link|code`)
- **Layout**: `ThemedView` with `type` for background colors. `Spacing` scale (half/one/two/three/four/five/six = 2/4/8/16/24/32/64)
- **External links**: `ExternalLink` wraps `expo-router` Link, opens in-app browser on native
- **Images**: `expo-image` for optimized images, static requires via `require()`
- **Animations**: `react-native-reanimated` for animations (FadeIn, etc.)
- **Safe area**: `react-native-safe-area-context` for platform-safe insets
- **Deep links**: `Linking.openURL()` for phone, mailto, maps URLs on native

### Platform Differences
- `*.web.tsx` files for web-specific overrides (e.g., `app-tabs.web.tsx`, `use-color-scheme.web.ts`)
- `Platform.select()` for conditional styles/logic
- Web badge shown on web only
- Drawer is native-only; web uses standard tab bar

### Assets
- `assets/expo.icon/` = iOS app icon directory
- `assets/images/` = splash screen, tab icons, tutorial images
- Android adaptive icons configured in `app.json`

## File Structure

```
src/
  app/
    _layout.tsx       # Root layout: ThemeProvider + Drawer (via withLayoutContext)
    index.tsx         # Home screen (tab bar + hamburger button)
    explore.tsx       # Explore screen
    sermons.tsx       # Sermon videos list
    doctrines.tsx     # Church beliefs/doctrines
    media.tsx         # Media gallery
    live-service.tsx  # Live streaming info
    donate.tsx        # Donation screen
    contact.tsx       # Contact info + maps deep link
  components/
    app-tabs.tsx           # Native tab bar (iOS/Android)
    app-tabs.web.tsx       # Web tab bar override
    animated-icon.tsx      # Animated logo component
    animated-icon.web.tsx
    external-link.tsx      # Cross-platform external link opener
    hint-row.tsx           # Dev hint UI component
    themed-text.tsx        # Themed Text wrapper
    themed-view.tsx        # Themed View wrapper
    ui/collapsible.tsx     # Expandable card with animation
    web-badge.tsx          # "Running on web" badge
  constants/
    theme.ts               # Colors, Fonts, Spacing, MaxContentWidth
  hooks/
    use-color-scheme.ts    # Re-export of react-native hook
    use-color-scheme.web.ts
    use-theme.ts           # Returns Colors[scheme]
  lib/
    api.ts                 # API client (donation, sermons, doctrines, contact)
```

## Mobile-Specific Constraints

- **No WebView**: Not installed. Use `Linking.openURL()` for maps and external content.
- **No react-native-svg**: Not installed. Use text/emoji for icons.
- **No shadcn/ui**: Web-only component library. Use `ThemedText`/`ThemedView` primitives.
- **No lucide-react**: Web-only icon library. Use emoji/unicode for icons.
- **Navigation**: Use `useNavigation()` + `router.push()` from `expo-router`. Open drawer via `(navigation as any).openDrawer()`.
- **API calls**: Use `fetch()` directly. No axios. Types in `src/lib/api.ts`.
- **Deep links**: `Linking.openURL('tel:...')`, `Linking.openURL('mailto:...')`, `Linking.openURL('https://maps.google.com/...')`.

## Commands

```bash
pnpm start           # Start dev server
pnpm android         # Android emulator/device
pnpm ios             # iOS simulator
pnpm web             # Web in browser
pnpm lint            # ESLint
pnpm reset-project   # Wipe app/ and start fresh
```

## Before Writing Code

1. Check Expo v56 docs: https://docs.expo.dev/versions/v56.0.0/
2. This is a **drawer-based** app. Hamburger menu opens the drawer for navigation.
3. Real church content goes in `src/app/` screens and components.
4. Backend API calls should go to the FastAPI backend at `/src/be/`.
5. Shared API types in `src/lib/api.ts`.
6. Mobile-specific components go in `src/components/`.
7. Consider mobile constraints: no web dependencies, use React Native primitives.

## Design Decisions

- `MaxContentWidth = 800` for centered content on wide screens
- `BottomTabInset`: iOS 50px, Android 80px (safe area padding)
- Tab icons use `renderingMode="template"` for tinting
- Splash screen background: `#208AEF` (Expo blue)
- App scheme: `afcmobile` (deep link URL scheme)
- Drawer type: `front` (slides in from right on iOS, from left on Android)
