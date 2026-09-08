"use client";

import FeatureFlagGuard from "@/components/feature-flag-guard";

export default function EventsLayout({ children }: { children: React.ReactNode }) {
  return (
      <FeatureFlagGuard flagName="enable_events">
        {children}
      </FeatureFlagGuard>
  );
}
