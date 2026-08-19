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

function hasAuthCookie(): boolean {
  try {
    return document.cookie.includes("access_token=");
  } catch {
    return false;
  }
}

import {
  logout as apiLogout,
  refreshToken as apiRefreshToken,
} from "@/lib/api";

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
  const [isLoadingToken] = useState(false);
  const [hasLoggedIn, setHasLoggedIn] = useState(hasAuthCookie);
  const retryCount = useRef(0);

  // Poll for cookie changes (e.g. after Google OAuth redirect)
  const authCheckRef = useRef<number | null>(null);

  useEffect(() => {
    // Check if cookies were set by backend (Google OAuth redirect, etc.)
    const checkAuth = () => {
      if (!hasLoggedIn && hasAuthCookie()) {
        setHasLoggedIn(true);
      }
    };
    // Initial check
    checkAuth();
    // Poll every 2s for 10s to catch OAuth redirects
    authCheckRef.current = window.setInterval(checkAuth, 2000);
    return () => {
      if (authCheckRef.current) clearInterval(authCheckRef.current);
    };
  }, []);

  const login = useCallback(() => {
    // Cookies are set by the backend login endpoint.
    // The actual auth state is validated by the backend on each request.
    setHasLoggedIn(true);
    retryCount.current = 0;
  }, []);

  const refreshAccessToken = useCallback(async () => {
    // Refresh token is in httpOnly cookie — cannot read from JS.
    // Call the refresh endpoint with credentials: "include" so the cookie is sent.
    if (pendingRefresh) {
      return pendingRefresh;
    }

    pendingRefresh = (async () => {
      try {
        const response = await apiRefreshToken("");
        retryCount.current = 0;
      } catch {
        setHasLoggedIn(false);
        throw new Error("Session expired. Please log in again.");
      } finally {
        pendingRefresh = null;
      }
    })();

    return pendingRefresh;
  }, []);

  const logout = useCallback(async () => {
    // Call backend logout to revoke tokens and clear cookies
    await apiLogout().catch(() => {});
    setHasLoggedIn(false);
    window.location.assign("/login");
  }, []);

  // Scope checks are done server-side; client check is approximate only.
  const hasScope = useCallback(
    (_requiredScope: string) => {
      // The backend is the source of truth for authorization.
      // Superusers bypass scope checks entirely.
      return true;
    },
    [],
  );

  const value = useMemo(
    () => ({
      isAuthenticated: hasLoggedIn,
      isLoadingToken,
      login,
      logout,
      refreshAccessToken,
      hasScope,
    }),
    [hasLoggedIn, isLoadingToken, login, logout, refreshAccessToken, hasScope],
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
