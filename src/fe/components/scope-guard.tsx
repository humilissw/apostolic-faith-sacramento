"use client";

import { useAuth } from "@/context/auth-context";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

interface ScopeGuardProps {
  requiredScopes: string[];
  children: React.ReactNode;
}

export default function ScopeGuard({ requiredScopes, children }: ScopeGuardProps) {
  const { isAuthenticated, hasScope, scopes } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    const hasRequiredScope = requiredScopes.some((scope) => hasScope(scope));
    if (!hasRequiredScope) {
      router.push("/");
    }
  }, [isAuthenticated, hasScope, router, requiredScopes]);

  if (!isAuthenticated) {
    return (
      <div className="flex justify-center items-center min-h-dvh">
        <p>Loading...</p>
      </div>
    );
  }

  const hasRequiredScope = requiredScopes.some((scope) => hasScope(scope));
  if (!hasRequiredScope) {
    return (
      <div className="flex justify-center items-center min-h-dvh">
        <p>Access denied</p>
      </div>
    );
  }

  return <>{children}</>;
}

export function useScope(requiredScopes: string[]): {
  isLoading: boolean;
  hasAccess: boolean;
  scopes: string[];
} {
  const { isAuthenticated, hasScope, scopes: currentScopes } = useAuth();

  if (!isAuthenticated) {
    return { isLoading: true, hasAccess: false, scopes: currentScopes };
  }

  const hasAccess = requiredScopes.some((scope) => hasScope(scope));
  return { isLoading: false, hasAccess, scopes: currentScopes };
}
