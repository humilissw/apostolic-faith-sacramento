import AuthGuard from "@/components/auth-guard";
import SuperuserGuard from "@/components/scope-guard";

export default function UsersAdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <SuperuserGuard requiredScopes={["users:admin"]}>{children}</SuperuserGuard>
    </AuthGuard>
  );
}
