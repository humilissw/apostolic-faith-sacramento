"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";

export default function SuperuserGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [isSuperuser, setIsSuperuser] = useState(false);

  useEffect(() => {
    async function check() {
      try {
        const res = await fetch(`${API_BASE}/api/v1/auth/me`, {
          credentials: "include",
        });
        if (!res.ok) {
          router.push("/login");
          return;
        }
        const data = await res.json();
        setIsSuperuser(data.is_superuser);
        if (!data.is_superuser) {
          router.push("/");
        }
      } catch {
        router.push("/login");
      } finally {
        setLoading(false);
      }
    }
    check();
  }, [router]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-dvh">
        <p>Loading...</p>
      </div>
    );
  }

  if (!isSuperuser) {
    return (
      <div className="flex justify-center items-center min-h-dvh">
        <p>Access denied</p>
      </div>
    );
  }

  return <>{children}</>;
}
