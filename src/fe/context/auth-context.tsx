"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  clearAllTokens,
  getAuthToken,
  getRefreshToken,
  revokeToken,
  setAuthToken,
  setRefreshToken,
  refreshToken as apiRefreshToken,
} from "@/lib/api";

interface AuthContextValue {
  token: string | null;
  scopes: string[];
  isAuthenticated: boolean;
  isLoadingToken: boolean;
  login: (access_token: string, refresh_token: string, scopes?: string[]) => void;
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<void>;
  hasScope: (requiredScope: string) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// Track ongoing refresh promises to avoid parallel refreshes
let pendingRefresh: Promise<void> | null = null;

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getAuthToken());
  const [isLoadingToken, setIsLoadingToken] = useState(true);
  const retryCount = useRef(0);

  const scopes = useMemo(() => {
    const stored = localStorage.getItem("auth_scopes");
    return stored ? JSON.parse(stored) : [];
  }, [token]);

  const isAuthenticated = token !== null;

  const login = useCallback((access_token: string, refresh_token: string, scopesInput?: string[]) => {
    setAuthToken(access_token);
    setRefreshToken(refresh_token);
    const storedScopes = scopesInput || ["api:all"];
    localStorage.setItem("auth_scopes", JSON.stringify(storedScopes));
    setToken(access_token);
    retryCount.current = 0;
  }, []);

  const refreshAccessToken = useCallback(async () => {
    const currentRefreshToken = getRefreshToken();
    if (!currentRefreshToken) {
      setToken(null);
      clearAllTokens();
      return;
    }

    // Deduplicate parallel refresh calls
    if (pendingRefresh) {
      return pendingRefresh;
    }

    try {
      const response = await apiRefreshToken(currentRefreshToken);
      setAuthToken(response.access_token);
      setToken(response.access_token);
      // The response doesn't include a new refresh token (server issues one)
      // We keep the existing refresh_token; the server handles rotation
      retryCount.current = 0;
    } catch {
      // Refresh failed — revoke and clear
      clearAllTokens();
      setToken(null);
      throw new Error("Session expired. Please log in again.");
    } finally {
      pendingRefresh = null;
    }
  }, []);

  const logout = useCallback(async () => {
    const currentToken = getAuthToken();
    const currentRefresh = getRefreshToken();
    // Fire-and-forget revoke (don't block the UI)
    if (currentRefresh) {
      revokeToken(currentRefresh).catch(() => {});
    } else if (currentToken) {
      revokeToken(currentToken).catch(() => {});
    }
    clearAllTokens();
    setToken(null);
  }, []);

  const hasScope = useCallback(
    (requiredScope: string) => {
      if (scopes.includes("api:all")) return true;
      if (scopes.includes(requiredScope)) return true;
      try {
        const t = getAuthToken();
        if (t) {
          const payload = JSON.parse(atob(t.split(".")[1]));
          if (payload.is_superuser) return true;
        }
      } catch {
        // ignore
      }
      return false;
    },
    [scopes],
  );

  const value = useMemo(
    () => ({
      token,
      isAuthenticated,
      isLoadingToken,
      login,
      logout,
      refreshAccessToken,
    hasScope,
    }),
    [token, isAuthenticated, isLoadingToken, login, logout, refreshAccessToken, scopes, hasScope],
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
