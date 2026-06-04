"use client";

import AuthGuard from "@/components/auth-guard";
import ScopeGuard from "@/components/scope-guard";
import FeatureFlagGuard from "@/components/feature-flag-guard";

export default function SchedulerCalendarLayout({ children }: { children: React.ReactNode }) {
  return (
    <FeatureFlagGuard flagName="enable_scheduler_calendar">
      <AuthGuard>
        <ScopeGuard requiredScopes={["member:limited"]}>{children}</ScopeGuard>
      </AuthGuard>
    </FeatureFlagGuard>
  );
}
