"use client";

import AuthGuard from "@/components/auth-guard";
import SuperuserGuard from "@/components/superuser-guard";
import FeatureFlagGuard from "@/components/feature-flag-guard";

export default function IntegrationsLayout({ children }: { children: React.ReactNode }) {
  return (
    <FeatureFlagGuard flagName="enable_integrations">
      <AuthGuard>
        <SuperuserGuard>{children}</SuperuserGuard>
      </AuthGuard>
    </FeatureFlagGuard>
  );
}
