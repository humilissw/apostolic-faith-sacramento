"use client";

import AuthGuard from "@/components/auth-guard";
import SuperuserGuard from "@/components/superuser-guard";

export default function EventsLayout({ children }: { children: React.ReactNode }) {
  return (
      <AuthGuard>
        <SuperuserGuard>{children}</SuperuserGuard>
      </AuthGuard>
  );
}
