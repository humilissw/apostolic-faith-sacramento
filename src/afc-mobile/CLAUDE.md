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
- `_layout.tsx` = root layout with `ThemeProvider` + `AppTabs`
- `index.tsx` = home screen
- `explore.tsx` = explore/info screen
- Tabs use `expo-router/unstable-native-tabs` (`NativeTabs`)
- Web routes handled via `expo-router` built-in web support

### Key Patterns
- **Theming**: `useTheme()` hook returns current Colors map (light/dark). `useColorScheme()` from react-native for raw scheme.
- **Typography**: `ThemedText` with `type` prop (`default|title|small|smallBold|subtitle|link|code`)
- **Layout**: `ThemedView` with `type` for background colors. `Spacing` scale (half/one/two/three/four/five/six = 2/4/8/16/24/32/64)
- **External links**: `ExternalLink` wraps `expo-router` Link, opens in-app browser on native
- **Images**: `expo-image` for optimized images, static requires via `require()`
- **Animations**: `react-native-reanimated` for animations (FadeIn, etc.)
- **Safe area**: `react-native-safe-area-context` for platform-safe insets

### Platform Differences
- `*.web.tsx` files for web-specific overrides (e.g., `app-tabs.web.tsx`, `use-color-scheme.web.ts`)
- `Platform.select()` for conditional styles/logic
- Web badge shown on web only

### Assets
- `assets/expo.icon/` = iOS app icon directory
- `assets/images/` = splash screen, tab icons, tutorial images
- Android adaptive icons configured in `app.json`

## File Structure

```
src/
  app/
    _layout.tsx    # Root layout: ThemeProvider + AppTabs
    index.tsx      # Home screen
    explore.tsx    # Explore screen
  components/
    app-tabs.tsx       # Native tab bar (iOS/Android)
    app-tabs.web.tsx   # Web tab bar override
    animated-icon.tsx  # Animated logo component
    animated-icon.web.tsx
    external-link.tsx  # Cross-platform external link opener
    hint-row.tsx       # Dev hint UI component
    themed-text.tsx    # Themed Text wrapper
    themed-view.tsx    # Themed View wrapper
    ui/collapsible.tsx # Expandable card with animation
    web-badge.tsx      # "Running on web" badge
  constants/
    theme.ts             # Colors, Fonts, Spacing, MaxContentWidth
  hooks/
    use-color-scheme.ts  # Re-export of react-native hook
    use-color-scheme.web.ts
    use-theme.ts         # Returns Colors[scheme]
```

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
2. This is a **template/starter** app. Currently shows Expo default screens.
3. Real church content goes in `src/app/` screens and components.
4. Backend API calls should go to the FastAPI backend at `/src/be/`.
5. Shared types/constants can live in a common package or be duplicated.

## Design Decisions

- `MaxContentWidth = 800` for centered content on wide screens
- `BottomTabInset`: iOS 50px, Android 80px (safe area padding)
- Tab icons use `renderingMode="template"` for tinting
- Splash screen background: `#208AEF` (Expo blue)
- App scheme: `afcmobile` (deep link URL scheme)
