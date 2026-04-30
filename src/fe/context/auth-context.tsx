"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";

import { clearAuthToken, getAuthToken, setAuthToken } from "@/lib/api";

interface AuthContextValue {
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getAuthToken());

  const isAuthenticated = token !== null;

  const login = useCallback((token: string) => {
    setAuthToken(token);
    setToken(token);
  }, []);

  const logout = useCallback(() => {
    clearAuthToken();
    setToken(null);
  }, []);

  const value = useMemo(
    () => ({ token, isAuthenticated, login, logout }),
    [token, isAuthenticated, login, logout],
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
