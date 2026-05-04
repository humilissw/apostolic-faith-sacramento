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

import { isAuthenticated, logout as apiLogout, refreshToken as apiRefreshToken } from "@/lib/api";

interface AuthContextValue {
  isAuthenticated: boolean;
  isLoadingToken: boolean;
  login: () => void;
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<void>;
  hasScope: (requiredScope: string) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// Track ongoing refresh promises to avoid parallel refreshes
let pendingRefresh: Promise<void> | null = null;

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isLoadingToken, setIsLoadingToken] = useState(true);
  const [tokenExpiry, setTokenExpiry] = useState<number | null>(null);
  const retryCount = useRef(0);

  // Authenticated if there's an auth cookie AND (either has a valid expiry or expiry hasn't been set yet, meaning the user just loaded the page)
  const isAuthenticatedState = document.cookie.includes("access_token=") && (tokenExpiry === null || tokenExpiry > Date.now());

  const login = useCallback(() => {
    // Cookies are set by the backend login endpoint.
    // Just need to set an initial expiry estimate (client doesn't have the exact value).
    // The actual auth state is validated by the backend on each request.
    setTokenExpiry(Date.now() + 600 * 1000); // 10 min default estimate
    retryCount.current = 0;
  }, []);

  const refreshAccessToken = useCallback(async () => {
    // Read refresh token from cookie
    const match = document.cookie.match(/refresh_token=([^;]+)/);
    const currentRefreshToken = match ? match[1] : null;
    if (!currentRefreshToken) {
      setTokenExpiry(null);
      return;
    }

    // Deduplicate parallel refresh calls
    if (pendingRefresh) {
      return pendingRefresh;
    }

    try {
      const response = await apiRefreshToken(currentRefreshToken);
      setTokenExpiry(Date.now() + response.access_token_expires * 1000);
      retryCount.current = 0;
    } catch {
      setTokenExpiry(null);
      throw new Error("Session expired. Please log in again.");
    } finally {
      pendingRefresh = null;
    }
  }, []);

  const logout = useCallback(async () => {
    // Call backend logout to revoke tokens and clear cookies
    await apiLogout().catch(() => {});
    setTokenExpiry(null);
    document.cookie = "auth_scopes=; max-age=0; path=/";
  }, []);

  const scopes = useMemo(() => {
    const stored = localStorage.getItem("auth_scopes");
    return stored ? JSON.parse(stored) : [];
  }, []);

  const hasScope = useCallback(
    (requiredScope: string) => {
      // Client-side scope check is approximate — the backend is the source of truth.
      // Superusers bypass scope checks entirely.
      if (scopes.includes("api:all")) return true;
      return scopes.includes(requiredScope);
    },
    [scopes],
  );

  // Check auth state on mount
  useEffect(() => {
    setIsLoadingToken(false);
  }, []);

  const value = useMemo(
    () => ({
      isAuthenticated: isAuthenticatedState,
      isLoadingToken,
      login,
      logout,
      refreshAccessToken,
      hasScope,
    }),
    [isAuthenticatedState, isLoadingToken, login, logout, refreshAccessToken, hasScope],
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
