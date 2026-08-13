# Frontend CLAUDE.md

## Project Overview

A Next.js 16 (App Router) web application for the Apostolic Faith Sacramento church. Static export build, deployed to localhost/out/. Uses React 19, HeroUI components, Tailwind CSS v4, and shadcn/ui primitives.

## Quick Start

```bash
# Setup
cd src/fe
bun install

# Run locally
bun dev

# Build (static export)
bun run build

# Test
bun test
bun test:watch

# Lint
bun lint
```

## Key Files

- `app/layout.tsx` - Root layout with providers
- `app/globals.css` - Global styles (Tailwind + CSS variables)
- `app/(main)/` - Main app pages (sermon, contact, doctrines, media, live-service)
- `app/(auth)/` - Auth pages (login)
- `components/navbar.tsx` - Navigation bar
- `components/footer.tsx` - Page footer
- `components/afc-logo.tsx` - Church logo component
- `components/sermon-videos.tsx` - Sermon video display
- `components/ui/` - shadcn/ui primitives (Radix-based)
- `hooks/` - Custom React hooks
- `lib/` - Utility functions (cn, class merging)
- `api.config.ts` - API configuration
- `envConfig.ts` - Environment variable handling
- `next.config.js` - Next.js config (static export output to out/)
- `tsconfig.json` - TypeScript (strict, ES2017 target, @/ path alias)

## Architecture Patterns

### Page Router Pattern

```tsx
// app/(main)/sermon/page.tsx
export default function SermonPage() {
  return (
    <main className="container mx-auto">
      <h1>Sermons</h1>
    </main>
  );
}
```

### Server vs Client Components

- **Server components by default** (no "use client" directive)
- Add `"use client"` only when needed (useState, useEffect, event handlers)

```tsx
// Server component (default)
export default function Page() {
  return <ClientComponent />;
}

// Client component - must be at top of file
"use client";

import { useState } from "react";
export default function ClientComponent() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

### Component Pattern

```tsx
// components/example.tsx
import { cn } from "@/lib/utils";

interface ExampleProps {
  title: string;
  variant?: "default" | "secondary";
  className?: string;
}

export function Example({ title, variant = "default", className }: ExampleProps) {
  return (
    <div className={cn(
      "px-4 py-2",
      variant === "secondary" && "bg-muted",
      className,
    )}>
      {title}
    </div>
  );
}
```

### Utility Functions

```tsx
// lib/utils.ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

### API Calls

Use server-side fetch or client-side hooks depending on context:

```tsx
// Server component - direct fetch
export default async function Page() {
  const res = await fetch("http://localhost:8000/api/...");
  const data = await res.json();
  return <div>{data}</div>;
}

// Client component - use custom hook
const { data, isLoading } = useApi("/api/...");
```

## Tech Stack

- **Framework**: Next.js 16 (App Router, React 19)
- **Language**: TypeScript 5.9+ (strict mode)
- **Styling**: Tailwind CSS v4 + `@tailwindcss/postcss`
- **Components**: HeroUI (`@heroui/react`) + shadcn/ui (Radix UI primitives)
- **Icons**: Lucide React + React Icons
- **Testing**: Jest + @testing-library/react
- **Linting**: ESLint + eslint-config-next
- **Build Output**: Static export to `out/`
- **Package Manager**: bun

## Environment

- `.env` - Local env vars
- `.env.local` - Local overrides
- `envConfig.ts` - Environment variable config
- `.env*` files should never be committed

## Static Export

Build output goes to `out/` directory. Deployed from `homepage` field in package.json (`localhost/out/`).

```bash
bun run build   # generates static files in out/
```

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

Test files in `__tests__/` alongside components. Jest config in `jest.config.js` + `jest.setup.js`.

## shadcn/ui

Components added via components.json (shadcn/ui config). Style: "new-york", Lucide icons, stone base color, CSS variables enabled.

```bash
# Add a component
npx shadcn@latest add button

# Add with bun
bunx shadcn@latest add button
```

## Gotchas

1. Use `cn()` from `@/lib/utils` for conditional class merging (never string concatenation)
2. Server components by default - add `"use client"` only when needed
3. Static export means no dynamic APIs (`next/navigation` router, `getServerSideProps`)
4. Path alias `@/*` maps to project root (see tsconfig.json paths)
5. All CSS variables use `stone` base color palette
6. HeroUI + shadcn/ui can have CSS conflicts - use specific selectors when needed
7. Use `await` for all async operations (fetch, database calls via API)

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [HeroUI Documentation](https://heroui.com/)
- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [Tailwind CSS v4 Documentation](https://tailwindcss.com/docs)
- [CLAUDE.md](./CLAUDE.md) - This file
- [AGENTS.md](./AGENTS.md) - Detailed agent guide
