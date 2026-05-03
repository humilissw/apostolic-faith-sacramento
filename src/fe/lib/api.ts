const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";
const API_V1 = "api/v1";

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  access_token_expires: number;
  refresh_token_expires: number;
}

export interface PkceChallenge {
  code_verifier: string;
  code_challenge: string;
  code_challenge_method: string;
}

export interface UpdateTokenResponse {
  access_token: string;
  token_type: string;
  access_token_expires: number;
}

// --- PKCE helpers ---

function generateRandomString(): string {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return btoa(String.fromCharCode(...array))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=/g, "");
}

export async function generatePkceChallenge(): Promise<PkceChallenge> {
  const code_verifier = generateRandomString();
  const encoder = new TextEncoder();
  const data = encoder.encode(code_verifier);
  const hash = await crypto.subtle.digest("SHA-256", data);
  const code_challenge = btoa(String.fromCharCode(...new Uint8Array(hash)))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=/g, "");
  return { code_verifier, code_challenge, code_challenge_method: "S256" };
}

// --- Token storage ---

function getStoredToken(key: string): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(key);
}

function setStoredToken(key: string, value: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(key, value);
}

function removeStoredToken(key: string): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(key);
}

export function getAuthToken(): string | null {
  return getStoredToken("auth_token");
}

export function getRefreshToken(): string | null {
  return getStoredToken("refresh_token");
}

export function setAuthToken(token: string): void {
  setStoredToken("auth_token", token);
}

export function setRefreshToken(token: string): void {
  setStoredToken("refresh_token", token);
}

export function clearAuthToken(): void {
  removeStoredToken("auth_token");
}

export function clearRefreshToken(): void {
  removeStoredToken("refresh_token");
}

export function clearAllTokens(): void {
  clearAuthToken();
  clearRefreshToken();
}

// --- API functions ---

export async function login(email: string, password: string): Promise<LoginResponse> {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);

  const res = await fetch(`${API_BASE}${API_V1}/login/access-token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData,
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Login failed");
  }

  return res.json();
}

export async function refreshToken(refresh_token: string): Promise<UpdateTokenResponse> {
  const res = await fetch(`${API_BASE}${API_V1}/login/refresh-token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token }),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Token refresh failed");
  }

  return res.json();
}

export async function revokeToken(token: string): Promise<void> {
  const res = await fetch(`${API_BASE}${API_V1}/login/revoke-token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });

  if (!res.ok) {
    // Don't throw on revoke failure — tokens are already gone locally
  }
}

export async function requestPkceChallenge(): Promise<PkceChallenge> {
  const res = await fetch(`${API_BASE}${API_V1}/login/pkce-challenge`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });

  if (!res.ok) {
    throw new Error("Failed to generate PKCE challenge");
  }

  return res.json();
}

export function googleLoginUrl(code_challenge: string): string {
  return `${API_BASE}${API_V1}/google/login/google?code_challenge=${encodeURIComponent(code_challenge)}&code_challenge_method=S256`;
}

// --- Auth-aware fetch ---

export async function fetchWithAuth(
  url: string,
  options: RequestInit = {},
  maxRetries: number = 1,
): Promise<Response> {
  let response = await fetch(url, options);

  // Retry once on 401 (access token expired) by refreshing
  if (response.status === 401 && maxRetries > 0) {
    const currentRefreshToken = getRefreshToken();
    if (currentRefreshToken) {
      try {
        const refreshed = await refreshToken(currentRefreshToken);
        setAuthToken(refreshed.access_token);

        // Clone headers and update Authorization with new token
        const newHeaders = { ...options.headers } as Record<string, string>;
        if (newHeaders["Authorization"]) {
          newHeaders["Authorization"] = `Bearer ${refreshed.access_token}`;
        }
        const newOptions: RequestInit = {
          ...options,
          headers: newHeaders,
        };
        response = await fetch(url, newOptions);
      } catch {
        // Refresh failed — user will be redirected to login by the context
      }
    }
  }

  return response;
}
