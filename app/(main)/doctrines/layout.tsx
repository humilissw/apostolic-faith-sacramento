"use client";

import FeatureFlagGuard from "@/components/feature-flag-guard";

export default function DoctrinesLayout({ children }: { children: React.ReactNode }) {
  return (
    <FeatureFlagGuard flagName="enable_doctrines">
      {children}
    </FeatureFlagGuard>
  );
}
