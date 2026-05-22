# Mobile App Architecture

**Rule**: Mobile app is Expo SDK 56 + React Native 0.85. Architecture is fundamentally different from web (Next.js). Never import web-only dependencies into mobile code.

**Why**: Mobile uses React Native primitives, not web DOM APIs. Mixing web dependencies breaks the build and causes runtime errors.

**How to apply**:
- Mobile: use `ThemedText`, `ThemedView`, `ScrollView`, `TouchableOpacity`, `Image` from `expo-image`
- Web: use `shadcn/ui`, `lucide-react`, `react-native-webview`, `react-native-svg`
- Mobile API client: `fetch()` directly, types in `src/lib/api.ts`
- Navigation: `expo-router` + `(navigation as any).openDrawer()` for drawer
- Deep links: `Linking.openURL('tel:...')`, `mailto:...`, `https://maps.google.com/...`
- Never import from `shadcn/ui`, `lucide-react`, `react-native-webview`, or `react-native-svg` into mobile components
