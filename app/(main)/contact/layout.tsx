"use client";

import FeatureFlagGuard from "@/components/feature-flag-guard";

export default function ContactLayout({ children }: { children: React.ReactNode }) {
  return (
    <FeatureFlagGuard flagName="enable_contact">
      {children}
    </FeatureFlagGuard>
  );
}
