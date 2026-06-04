"use client";

import AuthGuard from "@/components/auth-guard";
import SuperuserGuard from "@/components/scope-guard";
import FeatureFlagGuard from "@/components/feature-flag-guard";

export default function UsersAdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <FeatureFlagGuard flagName="enable_users_admin">
      <AuthGuard>
        <SuperuserGuard requiredScopes={["users:admin"]}>{children}</SuperuserGuard>
      </AuthGuard>
    </FeatureFlagGuard>
  );
}
