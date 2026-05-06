"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/auth-context";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";

function GoogleCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();
  const [error, setError] = useState("");

  useEffect(() => {
    async function handleCallback() {
      // Write scopes from URL to localStorage
      const scopesParam = searchParams.get("scopes");
      if (scopesParam) {
        try { localStorage.setItem("auth_scopes", JSON.stringify(scopesParam.split(",").filter(Boolean))); } catch { /* static export */ }
      }

      // Check if cookies were already validated by a previous pass
      if (searchParams.get("validated") === "true") {
        login();
        router.push("/");
        return;
      }

      // Verify the session cookies set by the backend are valid
      try {
        const res = await fetch(`${API_BASE}/api/v1/auth/me`, {
          method: "GET",
          credentials: "include",
        });

        if (!res.ok) {
          setError("Authentication failed — cookies invalid");
          setTimeout(() => router.push("/login"), 3000);
          return;
        }

        // Valid session — login and redirect
        login();
        // Avoid re-validation loops by not adding params
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
