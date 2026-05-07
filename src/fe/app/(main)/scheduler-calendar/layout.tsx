import AuthGuard from "@/components/auth-guard";
import ScopeGuard from "@/components/scope-guard";

export default function SchedulerCalendarLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <ScopeGuard requiredScopes={["member:limited"]}>{children}</ScopeGuard>
    </AuthGuard>
  );
}
