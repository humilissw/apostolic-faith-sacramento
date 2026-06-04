"use client";

import { useAuth } from "@/context/auth-context";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface ScopeGuardProps {
  requiredScopes: string[];
  children: React.ReactNode;
}

export default function ScopeGuard({ requiredScopes, children }: ScopeGuardProps) {
  const { isAuthenticated, hasScope, isLoadingToken } = useAuth();
  const router = useRouter();
  const [hasAccess, setHasAccess] = useState(false);
  const [loading, setLoading] = useState(true);

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (isLoadingToken) return;
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    // Check if user has at least one of the required scopes
    const allowed = requiredScopes.some((scope) => hasScope(scope));
    setHasAccess(allowed);
    setLoading(false);
    if (!allowed) {
      router.push("/");
    }
  /* eslint-enable react-hooks/set-state-in-effect */
  }, [isAuthenticated, hasScope, isLoadingToken, requiredScopes, router]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-dvh">
        <p>Loading...</p>
      </div>
    );
  }

  if (!hasAccess) {
    return (
      <div className="flex justify-center items-center min-h-dvh">
        <p>Access denied</p>
      </div>
    );
  }

  return <>{children}</>;
}

/* eslint-disable @typescript-eslint/no-unused-vars */
export function useScope(_requiredScopes: string[]): {
  isLoading: boolean;
  hasAccess: boolean;
} {
  const { isAuthenticated, isLoadingToken } = useAuth();
  if (isLoadingToken) return { isLoading: true, hasAccess: false };
  return { isLoading: false, hasAccess: !!isAuthenticated };
}
/* eslint-enable @typescript-eslint/no-unused-vars */
