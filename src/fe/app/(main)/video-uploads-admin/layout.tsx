import AuthGuard from "@/components/auth-guard";
import ScopeGuard from "@/components/scope-guard";

export default function VideoUploadsAdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <AuthGuard>
      <ScopeGuard requiredScopes={["video_uploads:manage"]}>{children}</ScopeGuard>
    </AuthGuard>
  );
}
