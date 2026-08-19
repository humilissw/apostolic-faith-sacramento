const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";
const API_V1 = "api/v1";

// --- PKCE helpers ---

export function generateRandomString(): string {
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

// --- Auth state detection (cookies are the source of truth) ---

function hasAuthCookie(): boolean {
  return document.cookie.includes("access_token=");
}

export function isAuthenticated(): boolean {
  return hasAuthCookie();
}

// --- Login API ---

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  access_token_expires: number;
  refresh_token_expires: number;
  scopes: string[];
}

export async function login(
  email: string,
  password: string,
  scopes: string[] = ["api:all"],
): Promise<LoginResponse> {
  const formData = new URLSearchParams();
  formData.append("username", email);
  formData.append("password", password);
  formData.append("scope", scopes.join(" "));

  const res = await fetch(`${API_BASE}${API_V1}/login/access-token`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: formData,
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Login failed");
  }

  return res.json();
}

// --- Token refresh ---

export interface UpdateTokenResponse {
  access_token: string;
  token_type: string;
  access_token_expires: number;
  scopes: string[];
}

export async function refreshToken(refresh_token: string): Promise<UpdateTokenResponse> {
  const res = await fetch(`${API_BASE}${API_V1}/login/refresh-token`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token }),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Token refresh failed");
  }

  return res.json();
}

export async function logout(): Promise<void> {
  const res = await fetch(`${API_BASE}${API_V1}/login/logout`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) {
    // Don't throw on logout failure — clear locally regardless
  }
}

export async function revokeToken(token: string): Promise<void> {
  const res = await fetch(`${API_BASE}${API_V1}/login/revoke-token`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token }),
  });

  if (!res.ok) {
    // Don't throw on revoke failure — tokens are already gone locally
  }
}

// --- Password Recovery / Reset API ---

export async function requestPasswordReset(email: string): Promise<{ message: string }> {
  const res = await fetch(`${API_BASE}${API_V1}/password-recovery`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to send password reset email");
  }

  return res.json();
}

export async function resetPassword(token: string, newPassword: string): Promise<{ message: string }> {
  const res = await fetch(`${API_BASE}${API_V1}/reset-password/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ token, new_password: newPassword }),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to reset password");
  }

  return res.json();
}

// --- Admin Password Reset API ---

export async function adminPasswordReset(email: string): Promise<{ message: string }> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/admin/password-reset`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to send admin password reset");
  }

  return res.json();
}

// --- PKCE challenge ---

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

// --- Auth-aware fetch (cookies auto-sent via credentials: "include") ---

export async function fetchWithAuth(
  url: string,
  options: RequestInit = {},
  maxRetries: number = 1,
): Promise<Response> {
  // Add Bearer token from localStorage (login page stores tokens there as JSON strings)
  const newOptions: RequestInit = { ...options, credentials: "include" };
  const accessToken = localStorage.getItem("access_token");
  if (accessToken) {
    try {
      newOptions.headers = { ...newOptions.headers, Authorization: `Bearer ${JSON.parse(accessToken)}` };
    } catch {
      // access_token may be a raw string
      newOptions.headers = { ...newOptions.headers, Authorization: `Bearer ${accessToken}` };
    }
  }

  let response = await fetch(url, newOptions);

  // Retry once on 401 (access token expired) by refreshing
  if (response.status === 401 && maxRetries > 0) {
    const currentRefreshToken = localStorage.getItem("refresh_token");
    if (currentRefreshToken) {
      try {
        await refreshToken(currentRefreshToken);
        // Cookies are updated by the backend refresh endpoint automatically
        // Retry with fresh cookies
        response = await fetch(url, { ...newOptions, credentials: "include" });
      } catch {
        // Refresh failed — user will be redirected to login by the context
      }
    }
  }

  return response;
}

// --- Auth types ---

export interface PkceChallenge {
  code_verifier: string;
  code_challenge: string;
  code_challenge_method: string;
}
