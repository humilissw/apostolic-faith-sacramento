"use client";

import { useAuth } from "@/context/auth-context";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoadingToken } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Wait for the initial /auth/me probe to settle before redirecting —
    // otherwise a valid session would bounce to /login on every load.
    if (!isLoadingToken && !isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, isLoadingToken, router]);

  if (isLoadingToken || !isAuthenticated) {
    return (
      <div className="flex justify-center items-center min-h-dvh">
        <p>Loading...</p>
      </div>
    );
  }

  return <>{children}</>;
}
