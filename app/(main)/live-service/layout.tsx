"use client";

import FeatureFlagGuard from "@/components/feature-flag-guard";

export default function LiveServiceLayout({ children }: { children: React.ReactNode }) {
  return (
    <FeatureFlagGuard flagName="enable_live_service">
      {children}
    </FeatureFlagGuard>
  );
}
