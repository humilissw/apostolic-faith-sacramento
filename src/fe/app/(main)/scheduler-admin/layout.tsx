"use client";

import AuthGuard from "@/components/auth-guard";
import ScopeGuard from "@/components/scope-guard";
import FeatureFlagGuard from "@/components/feature-flag-guard";

export default function SchedulerAdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <FeatureFlagGuard flagName="enable_scheduler_admin">
      <AuthGuard>
        <ScopeGuard requiredScopes={["scheduler:admin"]}>{children}</ScopeGuard>
      </AuthGuard>
    </FeatureFlagGuard>
  );
}
