"use client";

import AuthGuard from "@/components/auth-guard";
import SuperuserGuard from "@/components/scope-guard";
import FeatureFlagGuard from "@/components/feature-flag-guard";

export default function AdminPasswordResetLayout({ children }: { children: React.ReactNode }) {
  return (
    <FeatureFlagGuard flagName="enable_admin_password_reset">
      <AuthGuard>
        <SuperuserGuard requiredScopes={["superuser"]}>{children}</SuperuserGuard>
      </AuthGuard>
    </FeatureFlagGuard>
  );
}
