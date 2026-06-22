"use client";

import FeatureFlagGuard from "@/components/feature-flag-guard";

export default function ArchivedMediaLayout({ children }: { children: React.ReactNode }) {
  return (
    <FeatureFlagGuard flagName="enable_archived_media">
      {children}
    </FeatureFlagGuard>
  );
}
