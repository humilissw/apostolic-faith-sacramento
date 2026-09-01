"use client";

import { useAuth } from "@/context/auth-context";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function SuperuserGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, isLoadingToken, hasScope } = useAuth();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function check() {
      // Wait for the initial /auth/me probe (which also populates scopes).
      if (isLoadingToken) return;
      if (!isAuthenticated || !hasScope("superuser")) {
        router.push("/login");
        return;
      }
      setLoading(false);
    }
    check();
  }, [isAuthenticated, isLoadingToken, hasScope, router]);

  if (loading || isLoadingToken) {
    return (
      <div className="flex justify-center items-center min-h-dvh">
        <p>Loading...</p>
      </div>
    );
  }

  if (!hasScope("superuser")) {
    return (
      <div className="flex justify-center items-center min-h-dvh">
        <p>Access denied</p>
      </div>
    );
  }

  return <>{children}</>;
}
