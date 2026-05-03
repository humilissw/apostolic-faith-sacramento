"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { setRefreshToken } from "@/lib/api";

function GoogleCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();
  const [error, setError] = useState("");

  useEffect(() => {
    async function handleCallback() {
      const access_token = searchParams.get("access_token");
      const refresh_token = searchParams.get("refresh_token");

      if (!access_token || !refresh_token) {
        setError("Missing tokens from authentication server");
        setTimeout(() => router.push("/login"), 3000);
        return;
      }

      try {
        login(access_token, refresh_token);
        setRefreshToken(refresh_token);
        sessionStorage.removeItem("google_code_verifier");
        router.push("/");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Google login failed");
        setTimeout(() => router.push("/login"), 3000);
      }
    }

    handleCallback();
  }, [searchParams, login, router]);

  return (
    <div className="flex justify-center items-center min-h-dvh bg-zinc-100">
      <div className="text-center">
        {error ? (
          <>
            <p className="text-red-600 text-lg mb-4">{error}</p>
            <p className="text-zinc-500">Redirecting to login...</p>
          </>
        ) : (
          <p className="text-zinc-600 text-lg">Completing Google sign-in...</p>
        )}
      </div>
    </div>
  );
}

export default function GoogleCallbackPage() {
  return (
    <Suspense fallback={<p className="text-zinc-600 text-lg">Loading...</p>}>
      <GoogleCallbackContent />
    </Suspense>
  );
}
