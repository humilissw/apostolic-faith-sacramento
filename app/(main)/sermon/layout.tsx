"use client";

import FeatureFlagGuard from "@/components/feature-flag-guard";

export default function SermonLayout({ children }: { children: React.ReactNode }) {
  return (
    <FeatureFlagGuard flagName="enable_sermon">
      {children}
    </FeatureFlagGuard>
  );
}
