import AuthGuard from "@/components/auth-guard";
import ScopeGuard from "@/components/scope-guard";

export default function SchedulerAdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <ScopeGuard requiredScopes={["scheduler:admin"]}>{children}</ScopeGuard>
    </AuthGuard>
  );
}
