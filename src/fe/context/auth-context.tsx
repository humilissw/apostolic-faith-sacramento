"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import { fetchMe, logout as apiLogout, refreshToken as apiRefreshToken } from "@/lib/api";
import type { MeResponse } from "@/lib/api";

interface AuthContextValue {
  isAuthenticated: boolean;
  isLoadingToken: boolean;
  login: () => void;
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<void>;
  hasScope: (requiredScope: string) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// Track ongoing probes/refreshes to avoid parallel requests. The probe promise
// is shared at module level so every component that mounts in the same tick
// awaits one single /auth/me call.
let pendingProbe: Promise<void> | null = null;
let pendingRefresh: Promise<void> | null = null;

export function AuthProvider({ children }: { children: React.ReactNode }) {
  // The session lives in the BFF's signed cookie — nothing is readable from
  // JS, so auth state can only be established by asking the server. Start
  // "checking" (isLoadingToken=true) and resolve via GET /auth/me.
  const [isChecking, setIsChecking] = useState(true);
  const [hasLoggedIn, setHasLoggedIn] = useState(false);
  const [user, setUser] = useState<MeResponse | null>(null);
  const retryCount = useRef(0);

  const probe = useCallback(async () => {
    if (pendingProbe) return pendingProbe;
    pendingProbe = (async () => {
      try {
        const me = await fetchMe();
        setHasLoggedIn(me !== null);
        setUser(me);
        retryCount.current = 0;
      } catch {
        // Network failure — keep whatever state we had.
      } finally {
        setIsChecking(false);
        pendingProbe = null;
      }
    })();
    return pendingProbe;
  }, []);

  useEffect(() => {
    probe();
  }, [probe]);

  const login = useCallback(() => {
    // Called right after a successful login response (the session cookie is
    // already set by then). Re-probe so isAuthenticated flips immediately.
    retryCount.current = 0;
    void probe();
  }, [probe]);

  const refreshAccessToken = useCallback(async () => {
    if (pendingRefresh) {
      return pendingRefresh;
    }

    pendingRefresh = (async () => {
      try {
        await apiRefreshToken("");
        retryCount.current = 0;
      } catch {
        setHasLoggedIn(false);
        setUser(null);
        throw new Error("Session expired. Please log in again.");
      } finally {
        pendingRefresh = null;
      }
    })();

    return pendingRefresh;
  }, []);

  const logout = useCallback(async () => {
    await apiLogout().catch(() => {});
    setHasLoggedIn(false);
    setUser(null);
    window.location.assign("/login");
  }, []);

  // Scopes come from the /auth/me response (backend is the source of truth).
  // Superusers bypass scope checks entirely.
  const hasScope = useCallback(
    (requiredScope: string) => {
      if (!user) return false;
      const scopes = user.assigned_scopes ?? [];
      return scopes.includes("superuser") || scopes.includes(requiredScope);
    },
    [user],
  );

  const value = useMemo(
    () => ({
      isAuthenticated: hasLoggedIn,
      isLoadingToken: isChecking,
      login,
      logout,
      refreshAccessToken,
      hasScope,
    }),
    [hasLoggedIn, isChecking, login, logout, refreshAccessToken, hasScope],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used inside an AuthProvider");
  }
  return context;
}
