"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

const API_V1 = "api/v1";

interface FeatureFlagContextValue {
  flags: Record<string, boolean>;
  isLoading: boolean;
}

const FeatureFlagContext = createContext<FeatureFlagContextValue | undefined>(undefined);

export function FeatureFlagProvider({ children }: { children: React.ReactNode }) {
  const [flags, setFlags] = useState<Record<string, boolean>>({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function fetchFlags() {
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${API_V1}/feature-flags/`);
        if (!res.ok || cancelled) return;
        const data = await res.json();
        const flagMap: Record<string, boolean> = {};
        for (const flag of data.data) {
          flagMap[flag.name] = flag.is_enabled;
        }
        if (!cancelled) setFlags(flagMap);
      } catch {
        // Flags unavailable — all defaults to false
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
