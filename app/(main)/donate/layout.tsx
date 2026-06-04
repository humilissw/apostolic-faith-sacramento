"use client";

import FeatureFlagGuard from "@/components/feature-flag-guard";

export default function DonateLayout({ children }: { children: React.ReactNode }) {
  return (
    <FeatureFlagGuard flagName="enable_donate">
      {children}
    </FeatureFlagGuard>
  );
}
