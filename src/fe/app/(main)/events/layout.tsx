"use client";

import AuthGuard from "@/components/auth-guard";
import SuperuserGuard from "@/components/superuser-guard";
import FeatureFlagGuard from "@/components/feature-flag-guard";

export default function EventsLayout({ children }: { children: React.ReactNode }) {
  return (
      <FeatureFlagGuard flagName="enable_events">
        <AuthGuard>
          <SuperuserGuard>{children}</SuperuserGuard>
        </AuthGuard>
      </FeatureFlagGuard>
  );
}
