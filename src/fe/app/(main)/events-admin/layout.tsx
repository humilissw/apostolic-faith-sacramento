"use client";

import AuthGuard from "@/components/auth-guard";
import ScopeGuard from "@/components/scope-guard";
import FeatureFlagGuard from "@/components/feature-flag-guard";

export default function EventsLayout({ children }: { children: React.ReactNode }) {
  return (
      <FeatureFlagGuard flagName="enable_events_admin">
        <AuthGuard>
          <ScopeGuard requiredScopes={["events:admin"]}>{children}</ScopeGuard>
        </AuthGuard>
      </FeatureFlagGuard>
  );
}
