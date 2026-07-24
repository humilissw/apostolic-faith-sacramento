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

export interface FeatureFlagContextValue {
  flags: Record<string, boolean>;
  isLoading: boolean;
}

const FeatureFlagContext = createContext<FeatureFlagContextValue | undefined>(undefined);

// Default values -- all public feature flags true so the site works offline.
// Admin-only features default to false.
const DEFAULT_FLAGS: Record<string, boolean> = {
  // All public-facing features are enabled by default.
  // These can be overridden by flags-admin when a backend is running.
  enable_home: true,
  enable_sermon: true,
  enable_live_service: true,
  enable_features: true,
  enable_payments: true,
  enable_videos: true,
  enable_users_auth: true,
  // Public pages that didn't appear in the original list but have FeatureFlagGuard wrappers
  enable_doctrines: true,
  enable_media: true,
  enable_donate: true,
  enable_contact: true,
  // Admin features default to off when no backend exists
  enable_video_uploads_admin: false,
  enable_video_uploads: false,
  enable_scheduler_calendar: false,
  enable_scheduler_admin: false,
  enable_my_scheduler: false,
  enable_users_admin: false,
  enable_integrations: false,
  enable_flags_admin: false,
};

export function FeatureFlagProvider({ children }: { children: React.ReactNode }) {
  const [flags, setFlags] = useState<Record<string, boolean>>({ ...DEFAULT_FLAGS });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function fetchFlags() {
      try {
        const res = await fetch(`${API_BASE}${API_V1}/feature-flags/`);
        if (!res.ok || cancelled) return;
        const data = await res.json();
        const serverMap: Record<string, boolean> = {};
        for (const flag of data.data) {
          serverMap[flag.name] = flag.is_enabled;
        }
        if (!cancelled) setFlags((prev) => ({ ...prev, ...serverMap }));
      } catch {
        // Flags unavailable -- defaults take effect
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
