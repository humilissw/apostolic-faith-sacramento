const { hairlineWidth } = require('nativewind/theme');
const { Colors } = require('@/constants/theme');


/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  presets: [require('nativewind/preset')],
 theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: Colors.light.background,
          dark: Colors.dark.background,
        },
        foreground: {
          DEFAULT: Colors.light.foreground,
          dark: Colors.dark.foreground,
        },
        card: {
          DEFAULT: Colors.light.card,
          dark: Colors.dark.card,
          foreground: Colors.light.cardForeground,
          'foreground-dark': Colors.dark.cardForeground,
        },
        popover: {
          DEFAULT: Colors.light.popover,
          dark: Colors.dark.popover,
          foreground: Colors.light.popoverForeground,
          'foreground-dark': Colors.dark.popoverForeground,
        },
        primary: {
          DEFAULT: Colors.light.primary,
          dark: Colors.dark.primary,
          foreground: Colors.light.primaryForeground,
          'foreground-dark': Colors.dark.primaryForeground,
        },
        secondary: {
          DEFAULT: Colors.light.secondary,
          dark: Colors.dark.secondary,
          foreground: Colors.light.secondaryForeground,
          'foreground-dark': Colors.dark.secondaryForeground,
        },
        muted: {
          DEFAULT: Colors.light.muted,
          dark: Colors.dark.muted,
          foreground: Colors.light.mutedForeground,
          'foreground-dark': Colors.dark.mutedForeground,
        },
        accent: {
          DEFAULT: Colors.light.accent,
          dark: Colors.dark.accent,
          foreground: Colors.light.accentForeground,
          'foreground-dark': Colors.dark.accentForeground,
        },
        destructive: {
          DEFAULT: Colors.light.destructive,
          dark: Colors.dark.destructive,
          foreground: Colors.light.destructiveForeground,
          'foreground-dark': Colors.dark.destructiveForeground,
        },
        border: {
          DEFAULT: Colors.light.border,
          dark: Colors.dark.border,
        },
        input: {
          DEFAULT: Colors.light.input,
          dark: Colors.dark.input,
        },
        ring: {
          DEFAULT: Colors.light.ring,
          dark: Colors.dark.ring,
        },
        'background-element': {
          DEFAULT: Colors.light.backgroundElement,
          dark: Colors.dark.backgroundElement,
        },
        'background-selected': {
          DEFAULT: Colors.light.backgroundSelected,
          dark: Colors.dark.backgroundSelected,
        },
        'text-secondary': {
          DEFAULT: Colors.light.textSecondary,
          dark: Colors.dark.textSecondary,
        },
      },
    },
  },
  future: {
    hoverOnlyWhenSupported: true,
  },
  plugins: [require('tailwindcss-animate')],
};
