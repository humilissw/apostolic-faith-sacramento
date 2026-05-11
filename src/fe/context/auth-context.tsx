"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
} from "react";

function getLocalStorageItem(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch (err) {
    return null;
  }
}

function setLocalStorageItem(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch (err) {
    // localStorage unavailable (static export, private browsing)
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
  const hasCookie = (() => {
    try {
      return !!document.cookie.includes("access_token");
    } catch {
      return false;
    }
  })();
  const hasStoredToken = (() => {
    try {
      return !!localStorage.getItem("access_token");
    } catch {
      return false;
    }
  })();

  const [isLoadingToken] = useState(false);
  const [tokenExpiry, setTokenExpiry] = useState(() =>
    hasCookie || hasStoredToken ? Date.now() + 600 * 1000 : null,
  );
  const [hasLoggedIn, setHasLoggedIn] = useState(() => hasCookie || hasStoredToken);
  const retryCount = useRef(0);

  // Authenticated if user has successfully logged in AND token hasn't expired.
  // eslint-disable-next-line react-hooks/purity
  const tokenCheckTime = useMemo(() => Date.now(), []);
  const hasTokenExpired = tokenExpiry !== null && tokenExpiry < tokenCheckTime;
  const isAuthenticatedState = (hasLoggedIn || hasCookie) && (tokenExpiry === null || !hasTokenExpired);

  const login = useCallback(() => {
    // Cookies are set by the backend login endpoint.
    // Just need to set an initial expiry estimate (client doesn't have the exact value).
    // The actual auth state is validated by the backend on each request.
    setHasLoggedIn(true);
    setTokenExpiry(Date.now() + 600 * 1000); // 10 min default estimate
    retryCount.current = 0;
  }, []);

  const refreshAccessToken = useCallback(async () => {
    // Read refresh token from localStorage (where the login page stores it).
    // Cannot read httpOnly cookies from JS.
    const currentRefreshToken = getLocalStorageItem("refresh_token");
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
      setLocalStorageItem("auth_scopes", JSON.stringify(response.scopes));
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
    setHasLoggedIn(false);
    setTokenExpiry(null);
    setLocalStorageItem("auth_scopes", "[]");
    setLocalStorageItem("refresh_token", "");
    setLocalStorageItem("access_token", "");
    window.location.assign("/login")
  }, []);

  const scopes = useMemo(() => {
    const stored = getLocalStorageItem("auth_scopes");
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

  const value = useMemo(
    () => ({
      isAuthenticated: isAuthenticatedState,
      isLoadingToken,
      login,
      logout,
      refreshAccessToken,
      hasScope,
    }),
    [
      isAuthenticatedState,
      isLoadingToken,
      login,
      logout,
      refreshAccessToken,
      hasScope,
    ],
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
