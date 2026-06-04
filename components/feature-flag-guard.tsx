"use client";

import { useFeatureFlag } from "@/context/feature-flag-context";

interface FeatureFlagGuardProps {
  flagName: string;
  children: React.ReactNode;
}

export default function FeatureFlagGuard({ flagName, children }: FeatureFlagGuardProps) {
  const isFeatureEnabled = useFeatureFlag(flagName);

  if (!isFeatureEnabled) {
    return (
      <div className="flex justify-center items-center min-h-dvh">
        <p>Access denied</p>
      </div>
    );
  }

  return <>{children}</>;
}
