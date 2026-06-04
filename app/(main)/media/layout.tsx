"use client";

import FeatureFlagGuard from "@/components/feature-flag-guard";

export default function MediaLayout({ children }: { children: React.ReactNode }) {
  return (
    <FeatureFlagGuard flagName="enable_media">
      {children}
    </FeatureFlagGuard>
  );
}
