"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getAuthToken } from "@/lib/api";

interface SuperuserGuardProps {
  children: React.ReactNode;
}

function decodeJwtPayload(token: string): { is_superuser?: boolean } | null {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return { is_superuser: payload?.is_superuser };
  } catch {
    return null;
  }
}

export default function SuperuserGuard({ children }: SuperuserGuardProps) {
  const router = useRouter();

  useEffect(() => {
    const token = getAuthToken();
    if (!token) {
      router.push("/login");
      return;
    }

    const payload = decodeJwtPayload(token);
    if (!payload?.is_superuser) {
      router.push("/");
    }
  }, [router]);

  const token = getAuthToken();
  if (!token) {
    return (
      <div className="flex justify-center items-center min-h-dvh">
        <p>Loading...</p>
      </div>
    );
  }

  const payload = decodeJwtPayload(token);
  if (!payload?.is_superuser) {
    return (
      <div className="flex justify-center items-center min-h-dvh">
        <p>Access denied</p>
      </div>
    );
  }

  return <>{children}</>;
}
