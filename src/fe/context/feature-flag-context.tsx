"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";
const API_V1 = "api/v1";

interface FeatureFlagContextValue {
  flags: Record<string, boolean>;
  isLoading: boolean;
}

const FeatureFlagContext = createContext<FeatureFlagContextValue | undefined>(undefined);

// Default feature flag values when the backend is unreachable.
// Public-facing features default to true so the site remains usable.
// Admin-only features default to false for safety.
const DEFAULT_FLAGS: Record<string, boolean> = {
  enable_home: true,
  enable_doctrines: true,
  enable_contact: true,
  enable_media: true,
  enable_donate: false,
  enable_sermon: true,
  enable_live_service: true,
  // Admin features default to disabled when backend is unreachable
  enable_video_uploads: false,
  enable_scheduler_calendar: false,
  enable_scheduler_admin: false,
  enable_my_scheduler: false,
  enable_users_admin: false,
  enable_video_uploads_admin: false,
  enable_integrations: false,
  enable_flags_admin: false,
  enable_admin_password_reset: false,
};

export function FeatureFlagProvider({ children }: { children: React.ReactNode }) {
  const [flags, setFlags] = useState<Record<string, boolean>>(DEFAULT_FLAGS);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function fetchFlags() {
      try {
        const res = await fetch(`${API_BASE}${API_V1}/feature-flags/`);
        if (!res.ok || cancelled) return;
        const data = await res.json();
        const flagMap: Record<string, boolean> = {};
        for (const flag of data.data) {
          flagMap[flag.name] = flag.is_enabled;
        }
        // Merge with defaults so admin-only flags are still available if the API
        // returns a partial list.
        if (!cancelled) setFlags((prev) => ({ ...DEFAULT_FLAGS, ...flagMap }));
      } catch {
        // Backend unreachable — keep default values (public features enabled,
        // admin features disabled). This ensures the site remains usable.
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    fetchFlags();
    return () => { cancelled = true; };
  }, []);

  const value = useMemo(
    () => ({ flags, isLoading }),
    [flags, isLoading],
  );

  return <FeatureFlagContext.Provider value={value}>{children}</FeatureFlagContext.Provider>;
}

export function useFeatureFlag(name: string): boolean {
  const context = useContext(FeatureFlagContext);
  if (context === undefined) {
    throw new Error("useFeatureFlag must be used inside a FeatureFlagProvider");
  }
  return context.flags[name] ?? false;
}

export function useFeatureFlags(): {
  flags: Record<string, boolean>;
  isLoading: boolean;
} {
  const context = useContext(FeatureFlagContext);
  if (context === undefined) {
    throw new Error("useFeatureFlags must be used inside a FeatureFlagProvider");
  }
  return { flags: context.flags, isLoading: context.isLoading };
}
