/**
 * Below are the colors that are used in the app. The colors are defined in the light and dark mode.
 * There are many other ways to style your app. For example, [Nativewind](https://www.nativewind.dev/), [Tamagui](https://tamagui.dev/), [unistyles](https://reactnativeunistyles.vercel.app), etc.
 */

import { Platform } from 'react-native';

export const Colors = {
  light: {
    // Base
    background: '#ffffff',
    foreground: '#000000',
 
    // Card
    card: '#ffffff',
    cardForeground: '#000000',
 
    // Popover / dropdown
    popover: '#ffffff',
    popoverForeground: '#000000',
 
    // Primary action (buttons, links)
    primary: '#1a1a1a',
    primaryForeground: '#fafafa',
 
    // Secondary action (ghost buttons, badges)
    secondary: '#f4f4f5',
    secondaryForeground: '#1a1a1a',
 
    // Muted (placeholders, subtle backgrounds)
    muted: '#f4f4f5',
    mutedForeground: '#71717a',
 
    // Accent (hover states, highlights)
    accent: '#f4f4f5',
    accentForeground: '#1a1a1a',
 
    // Destructive (errors, delete actions)
    destructive: '#ef4444',
    destructiveForeground: '#fafafa',
 
    // Border & input
    border: '#e4e4e7',
    input: '#e4e4e7',
    ring: '#1a1a1a',
 
    // Custom
    backgroundElement: '#F0F0F3',
    backgroundSelected: '#E0E1E6',
    textSecondary: '#60646C',
  },
 
  dark: {
    // Base
    background: '#000000',
    foreground: '#ffffff',
 
    // Card
    card: '#0a0a0a',
    cardForeground: '#ffffff',
 
    // Popover / dropdown
    popover: '#0a0a0a',
    popoverForeground: '#ffffff',
 
    // Primary action (buttons, links)
    primary: '#fafafa',
    primaryForeground: '#1a1a1a',
 
    // Secondary action (ghost buttons, badges)
    secondary: '#27272a',
    secondaryForeground: '#fafafa',
 
    // Muted (placeholders, subtle backgrounds)
    muted: '#27272a',
    mutedForeground: '#a1a1aa',
 
    // Accent (hover states, highlights)
    accent: '#27272a',
    accentForeground: '#fafafa',
 
    // Destructive (errors, delete actions)
    destructive: '#7f1d1d',
    destructiveForeground: '#fafafa',
 
    // Border & input
    border: '#27272a',
    input: '#27272a',
    ring: '#d4d4d8',
 
    // Custom
    backgroundElement: '#212225',
    backgroundSelected: '#2E3135',
    textSecondary: '#B0B4BA',
  },
} as const;

export type ThemeColor = keyof typeof Colors.light & keyof typeof Colors.dark;

export const Fonts = Platform.select({
  ios: {
    /** iOS `UIFontDescriptorSystemDesignDefault` */
    sans: 'system-ui',
    /** iOS `UIFontDescriptorSystemDesignSerif` */
    serif: 'ui-serif',
    /** iOS `UIFontDescriptorSystemDesignRounded` */
    rounded: 'ui-rounded',
    /** iOS `UIFontDescriptorSystemDesignMonospaced` */
    mono: 'ui-monospace',
  },
  default: {
    sans: 'normal',
    serif: 'serif',
    rounded: 'normal',
    mono: 'monospace',
  },
  web: {
    sans: 'var(--font-display)',
    serif: 'var(--font-serif)',
    rounded: 'var(--font-rounded)',
    mono: 'var(--font-mono)',
  },
});

export const Spacing = {
  half: 2,
  one: 4,
  two: 8,
  three: 16,
  four: 24,
  five: 32,
  six: 64,
} as const;

export const BottomTabInset = Platform.select({ ios: 50, android: 80 }) ?? 0;
export const MaxContentWidth = 800;
