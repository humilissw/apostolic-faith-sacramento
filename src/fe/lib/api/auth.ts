const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";
const API_V1 = "api/v1";

// The SPA talks to the BFF (Flask) which sits in front of the FastAPI backend.
// Auth is owned by the BFF server-side: it keeps the JWTs in a signed session
// cookie and injects them on every forwarded /api/v1/* call. The browser never
// sees a token — so there is no localStorage token handling here anymore.
const BFF_AUTH = "auth";

function bffBase(): string {
  // Normalize trailing slash: API_BASE may be "https://host:8002/" or ".../api"
  return API_BASE.endsWith("/") ? API_BASE : `${API_BASE}/`;
}

// --- PKCE helpers (Google OAuth — kept for the direct-backend flow) ---

export function generateRandomString(): string {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return btoa(String.fromCharCode(...array))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
}

export async function generatePkceChallenge(): Promise<PkceChallenge> {
  const code_verifier = generateRandomString();
  const encoder = new TextEncoder();
  const data = encoder.encode(code_verifier);
  const hash = await crypto.subtle.digest("SHA-256", data);
  const code_challenge = btoa(String.fromCharCode(...new Uint8Array(hash)))
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/, "");
  return { code_verifier, code_challenge, code_challenge_method: "S256" };
}

// --- Login API (BFF-first with direct-backend fallback) ---

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  access_token_expires: number;
  refresh_token_expires: number;
  scopes: string[];
}

/**
 * Log in via the BFF (`POST /auth/login?redirect=false`). The BFF authenticates
 * against the backend, stores the tokens in its signed session cookie, and
 * returns a one-time code. `credentials: "include"` carries that cookie back to
 * the browser, which is all subsequent requests need.
 *
 * If the endpoint does not exist (SPA pointed directly at the FastAPI backend),
 * fall back to the raw password grant so both topologies keep working.
 */
export async function login(
  email: string,
  password: string,
  scopes: string[] = ["api:all"],
): Promise<LoginResponse> {
  const bffRes = await fetch(`${bffBase()}${BFF_AUTH}/login?redirect=false`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username: email, password }),
  });

  if (bffRes.ok) {
    // BFF established the session. The token fields are not exposed to the
    // browser by design — return a minimal shape for callers that read it.
    const json = await bffRes.json().catch(() => ({}));
    return {
      access_token: "",
      refresh_token: "",
      token_type: "bearer",
      access_token_expires: 0,
      refresh_token_expires: 0,
      scopes: json.scopes ?? scopes,
      ...(json as object),
    } as LoginResponse;
  }

  // Fallback: no BFF in front (direct backend). Password grant with cookies.
  if (bffRes.status === 404 || bffRes.status === 501) {
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

  // BFF rejected the credentials — surface its error verbatim.
  const body = await bffRes.text();
  throw new Error(body || "Login failed");
}

// --- Token refresh (BFF-first with direct-backend fallback) ---

export interface UpdateTokenResponse {
  access_token: string;
  token_type: string;
  access_token_expires: number;
  scopes: string[];
}

/**
 * Refresh the session. Via the BFF this calls `POST /auth/refresh`, which uses
 * the refresh token stored in the BFF's own session — no token ever crosses to
 * the browser. In direct-backend mode the backend reads its httpOnly cookie.
 */
export async function refreshToken(_refresh_token: string = ""): Promise<UpdateTokenResponse> {
  const bffRes = await fetch(`${bffBase()}${BFF_AUTH}/refresh`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: "{}",
  });

  if (bffRes.ok) {
    return bffRes.json().catch(() => ({
      access_token: "",
      token_type: "bearer",
      access_token_expires: 0,
      scopes: [],
    }));
  }

  if (bffRes.status === 404 || bffRes.status === 501) {
    const res = await fetch(`${API_BASE}${API_V1}/login/refresh-token`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: _refresh_token }),
    });
    if (!res.ok) {
      const body = await res.text();
      throw new Error(body || "Token refresh failed");
    }
    return res.json();
  }

  const body = await bffRes.text();
  throw new Error(body || "Token refresh failed");
}

// --- Logout (BFF-first with direct-backend fallback) ---

export async function logout(): Promise<void> {
  try {
    const bffRes = await fetch(`${bffBase()}${BFF_AUTH}/logout`, {
      method: "POST",
      credentials: "include",
    });
    if (bffRes.ok || bffRes.status === 401) {
      return; // BFF handled it (401 = session already gone, still fine)
    }
    if (bffRes.status !== 404 && bffRes.status !== 501) {
      return; // BFF present but errored — don't double-logout on the backend
    }
  } catch {
    return; // network error — nothing to revoke client-side anyway
  }

  const res = await fetch(`${API_BASE}${API_V1}/login/logout`, {
    method: "POST",
    credentials: "include",
  }).catch(() => null);
  if (res && !res.ok) {
    // Don't throw on logout failure — clear locally regardless
  }
}

// --- Current user (the BFF is the source of truth for auth state) ---

export interface MeResponse {
  email: string;
  full_name?: string;
  id?: string;
  is_active?: boolean;
  assigned_scopes?: string[];
}

/**
 * Ask "who am I?" — via `GET /auth/me` on the BFF, which validates (and
 * silently refreshes) the session server-side. This replaces the old
 * `document.cookie` sniffing: the backend's token cookies are httpOnly and can
 * never be read from JS, so cookie-sniffing was always wrong.
 */
export async function fetchMe(): Promise<MeResponse | null> {
  const res = await fetch(`${bffBase()}${BFF_AUTH}/me`, {
    method: "GET",
    credentials: "include",
  });
  if (res.ok) return res.json();
  // No BFF in front (direct backend): the httpOnly cookies still authenticate.
  if (res.status === 404 || res.status === 501) {
    const direct = await fetch(`${API_BASE}${API_V1}/auth/me`, {
      method: "GET",
      credentials: "include",
    });
    if (!direct.ok) return null;
    return direct.json();
  }
  return null;
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

// --- PKCE challenge (direct-backend Google flow) ---

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

// --- Auth-aware fetch (session cookie auto-sent via credentials: "include") ---

export async function fetchWithAuth(
  url: string,
  options: RequestInit = {},
  maxRetries: number = 1,
): Promise<Response> {
  // No client-side Authorization header: when the BFF is in front it injects
  // the access token server-side; in direct-backend mode the httpOnly cookies
  // carry the session. credentials: "include" covers both cases.
  const newOptions: RequestInit = { ...options, credentials: "include" };

  let response = await fetch(url, newOptions);

  // Retry once on 401 (access token expired) by refreshing. Via the BFF the
  // refresh uses its stored refresh token; in direct-backend mode the backend
  // reads its httpOnly cookie automatically and rotates both cookies.
  if (response.status === 401 && maxRetries > 0) {
    try {
      await refreshToken("");
      response = await fetch(url, newOptions);
    } catch {
      // Refresh failed — user will be redirected to login by the context
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
