# AGENTS.md

High-level overview of the Apostolic Faith Sacramento frontend project and development patterns.

## Project Overview

A Next.js static website for the Apostolic Faith Sacramento church, featuring sermon pages, media gallery, doctrine pages, contact form, and live service streaming. Built as a static export for simple deployment.

## Architecture

### Tech Stack

- **Framework**: Next.js 16 (App Router, React 19)
- **Language**: TypeScript 5.9+ (strict mode)
- **Styling**: Tailwind CSS v4 + @tailwindcss/postcss
- **Components**: HeroUI + shadcn/ui (Radix UI)
- **Icons**: Lucide React + React Icons
- **Testing**: Jest + @testing-library/react
- **Linting**: ESLint + eslint-config-next
- **Package Manager**: bun

### Project Structure

```
fe/
├── app/
│   ├── (auth)/              # Auth route group
│   │   └── login/           # Login page
│   ├── (main)/              # Main app route group
│   │   ├── page.tsx         # Home page
│   │   ├── sermon/          # Sermon page
│   │   ├── media/           # Media gallery
│   │   ├── doctrines/       # Doctrine pages
│   │   ├── contact/         # Contact page
│   │   ├── live-service/    # Live streaming page
│   │   ├── donate/          # Donation page
│   │   ├── integrations/    # Integration pages
│   │   ├── users-admin/     # User admin panel
│   │   ├── video-uploads/   # Video uploads
│   │   ├── video-uploads-admin/  # Video upload admin
│   │   ├── scheduler-admin/     # Scheduler admin
│   │   ├── scheduler-calendar/  # Calendar view
│   │   ├── my-scheduler/        # My scheduler (user)
│   │   └── flags-admin/         # Feature flag admin
│   ├── layout.tsx           # Root layout
│   ├── globals.css          # Global styles
│   └── not-found.tsx        # 404 page
├── components/
│   ├── ui/                  # shadcn/ui primitives
│   ├── navbar.tsx           # Navigation bar
│   ├── footer.tsx           # Page footer
│   ├── afc-logo.tsx         # Church logo
│   ├── sermon-videos.tsx    # Sermon video component
│   └── ...                  # Other shared components
├── hooks/                   # Custom React hooks
├── lib/                     # Utility functions
│   └── utils.ts             # cn() helper
├── __tests__/               # Test files
├── public/                  # Static assets
├── next.config.js           # Next.js config
├── tsconfig.json            # TypeScript config
├── package.json             # Dependencies
└── components.json          # shadcn/ui config
```

## Development Patterns

### 1. Page Structure

All pages use the App Router file-based routing:

```tsx
// app/(main)/sermon/page.tsx
import { SermonVideos } from "@/components/sermon-videos";

export default function SermonPage() {
  return (
    <main className="min-h-screen">
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold">Sermons</h1>
        <SermonVideos />
      </div>
    </main>
  );
}
```

### 2. Component Patterns

#### Server Components (default)

```tsx
// No "use client" directive - server component
export async function Page() {
  const data = await fetchData();
  return <div>{data.title}</div>;
}
```

#### Client Components

```tsx
"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";

export function Counter() {
  const [count, setCount] = useState(0);
  return (
    <Button onClick={() => setCount(count + 1)}>
      Count: {count}
    </Button>
  );
}
```

### 3. Styling

Always use Tailwind classes + `cn()` for conditional styles:

```tsx
import { cn } from "@/lib/utils";

<div className={cn(
  "px-4 py-2 rounded-lg",
  isActive && "bg-primary text-primary-foreground",
  variant === "secondary" && "bg-muted",
)}>
  Content
</div>
```

### 4. shadcn/ui Component Usage

Components are imported from `@/components/ui/`:

```tsx
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
```

### 5. HeroUI Component Usage

HeroUI components for larger UI patterns:

```tsx
import { Dropdown, DropdownTrigger, DropdownMenu, DropdownItem } from "@heroui/dropdown";
import { Chip } from "@heroui/react";
```

### 6. Utility Functions

The `cn()` helper merges Tailwind classes safely:

```tsx
import { cn } from "@/lib/utils";

// Usage
cn("base-class", condition && "conditional-class", className);
```

## Configuration

### TypeScript

- Strict mode enabled
- Path alias: `@/*` maps to project root
- Target: ES2017
- JSX: react-jsx

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "paths": {
      "@/*": ["./*"]
    },
    "jsx": "react-jsx"
  }
}
```

### Environment Variables

Local env vars in `.env` or `.env.local`. Never commit these files.

### shadcn/ui

Configured in `components.json`:
- Style: "new-york"
- Icons: Lucide
- Base color: stone
- CSS variables: enabled

## Testing

```bash
# Run all tests
bun test

# Watch mode
bun test:watch

# CI mode
bun test:ci

# Update snapshots
bun run snapshot-update
```

Test files live in `__tests__/` alongside components. Jest config in `jest.config.js` + `jest.setup.js`.

```tsx
// __tests__/example.test.tsx
import { render, screen } from "@testing-library/react";
import { Example } from "@/components/example";

describe("Example", () => {
  it("renders the title", () => {
    render(<Example title="Hello" />);
    expect(screen.getByText("Hello")).toBeInTheDocument();
  });
});
```

## Build & Deployment

Static export output goes to `out/`:

```bash
bun build   # generates static files
bun start   # starts dev server (not for production)
```

The `out/` directory contains the fully static site ready for deployment.

Docker builds use bun as the package manager (pinned via the `packageManager` field in package.json) and run the container with `bun https` — the Next.js dev server with experimental HTTPS (certs in `security_keys/`) on port 3000. There is no nginx; bun serves the app directly.

## Common Gotchas

### Static Export Limitations

- No dynamic routes (`[id]`)
- No `next/navigation` router APIs in server components
- No API routes (use backend API directly)
- Use `generateStaticParams()` for dynamic-like pages

### CSS Conflicts

- HeroUI and shadcn/ui may have conflicting styles - always scope selectors
- Use `cn()` for all conditional classes (never string concatenation)
- Global styles in `globals.css` are shared across all pages

### TypeScript Strict Mode

- All components must be typed (no `any`)
- Use `interface` for props, `type` for utilities
- Path aliases work with `@/` prefix

### Environment

- `.env*` files should never be committed
- Backend API URL should be configurable via env vars
- Check `.env` and `.env.local` for available variables

### shadcn/ui Additions

- New UI components are added via `bunx shadcn@latest add <component>`
- Components go to `components/ui/` automatically
- Check `components.json` for available aliases

## Next Steps for New Agents

1. Read this file first
2. Check `app/(main)/` pages for existing page structure
3. Review `components/ui/` for available shadcn/ui primitives
4. Look at `lib/utils.ts` for utility functions
5. Check `.env` for configuration
6. Run `bun test` to verify nothing is broken
7. Use `cn()` for all class name merging
