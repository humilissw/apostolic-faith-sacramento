const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";
const API_V1 = "api/v1";

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  access_token_expires: number;
  refresh_token_expires: number;
  scopes: string[];
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
  scopes: string[];
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
  removeStoredToken("auth_scopes");
}

export function getScopesFromToken(token: string): string[] {
  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    return (payload.scopes as string[]) || [];
  } catch {
    return [];
  }
}

// --- API functions ---

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
  const token = getAuthToken();
  const existingHeaders = { ...(options.headers as Record<string, string> || {}) };
  const headers = token
    ? { ...existingHeaders, Authorization: `Bearer ${token}` }
    : existingHeaders;
  const newOptions: RequestInit = { ...options, headers };

  let response = await fetch(url, newOptions);

  // Retry once on 401 (access token expired) by refreshing
  if (response.status === 401 && maxRetries > 0) {
    const currentRefreshToken = getRefreshToken();
    if (currentRefreshToken) {
      try {
        const refreshed = await refreshToken(currentRefreshToken);
        setAuthToken(refreshed.access_token);

        const newHeaders = { ...headers, Authorization: `Bearer ${refreshed.access_token}` };
        const newOpts: RequestInit = { ...newOptions, headers: newHeaders };
        response = await fetch(url, newOpts);
      } catch {
        // Refresh failed — user will be redirected to login by the context
      }
    }
  }

  return response;
}

// --- Payment / Donation API functions ---

export interface DonationFormData {
  amount_cents: number;
  currency: string;
  frequency: "one_time" | "recurring";
  donor_email?: string;
  donor_name?: string;
}

export interface PaymentIntentResult {
  client_secret: string;
  payment_intent_id: string;
}

export interface CheckoutSessionResult {
  client_secret: string;
  type: "checkout";
  checkout_url: string;
}

export interface DonationConfig {
  id: string;
  label: string;
  amount_cents: number;
  is_default: boolean;
  frequency: "one_time" | "recurring";
  created_on: string;
}

export interface PaymentRecord {
  id: string;
  amount_cents: number;
  currency: string;
  status: string;
  stripe_payment_intent_id: string;
  stripe_subscription_id: string | null;
  donor_email: string | null;
  donor_name: string | null;
  receipt_url: string | null;
  created_on: string;
  updated_on: string | null;
}

export async function createPaymentIntent(data: DonationFormData): Promise<PaymentIntentResult> {
  const res = await fetch(`${API_BASE}${API_V1}/payments/create-intent`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to create payment intent");
  }

  return res.json();
}

export async function createSubscription(data: DonationFormData): Promise<CheckoutSessionResult> {
  const res = await fetch(`${API_BASE}${API_V1}/payments/create-subscription`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to create subscription");
  }

  return res.json();
}

export async function fetchDonationConfigs(): Promise<DonationConfig[]> {
  const res = await fetch(`${API_BASE}${API_V1}/payments/config`);
  if (!res.ok) {
    throw new Error("Failed to fetch donation configs");
  }
  const body = await res.json();
  return body.data;
}

export async function fetchUserPayments(): Promise<{ data: PaymentRecord[]; count: number }> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/payments/`);
  if (!res.ok) {
    throw new Error("Failed to fetch payments");
  }
  return res.json();
}

// --- Integration API functions ---

export interface IntegrationConfig {
  id: string;
  type: string;
  display_name: string;
  icon: string;
  enabled: boolean;
  status: string;
  last_synced_at: string | null;
  config_json: string | null;
  created_on: string;
  updated_on: string | null;
}

export interface IntegrationCredentialField {
  type: string;
  fields: Record<string, string>;
}

export interface IntegrationWithCreds extends IntegrationConfig {
  credential_fields: Record<string, string>;
}

export interface IntegrationsResponse {
  data: IntegrationConfig[];
  count: number;
}

export interface TestConnectionResult {
  success: boolean;
  status: string;
  message: string;
}

export async function fetchIntegrationsStatus(): Promise<Record<string, { enabled: boolean; status: string }>> {
  const res = await fetch(`${API_BASE}${API_V1}/integrations/status`);
  if (!res.ok) {
    throw new Error("Failed to fetch integration status");
  }
  return res.json();
}

export async function fetchIntegrations(): Promise<IntegrationsResponse> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/integrations/`);
  if (!res.ok) {
    throw new Error("Failed to fetch integrations");
  }
  return res.json();
}

export async function fetchIntegration(id: string): Promise<IntegrationWithCreds> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/integrations/${id}`);
  if (!res.ok) {
    throw new Error("Failed to fetch integration");
  }
  return res.json();
}

export async function createIntegration(data: {
  type: string;
  display_name: string;
  icon: string;
  enabled: boolean;
  config_json?: string | null;
  credentials: Record<string, string>;
}): Promise<IntegrationWithCreds> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/integrations/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to create integration");
  }
  return res.json();
}

export async function updateIntegration(id: string, data: Partial<{
  display_name: string;
  icon: string;
  enabled: boolean;
  status: string;
  config_json: string | null;
}>): Promise<IntegrationWithCreds> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/integrations/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to update integration");
  }
  return res.json();
}

export async function updateIntegrationCredentials(
  id: string,
  credentials: Record<string, string>,
): Promise<IntegrationWithCreds> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/integrations/${id}/credentials`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ credentials }),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to update credentials");
  }
  return res.json();
}

export async function deleteIntegration(id: string): Promise<void> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/integrations/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to delete integration");
  }
}

export async function testIntegrationConnection(data: {
  type: string;
  credentials: Record<string, string>;
  config_json?: string | null;
}): Promise<TestConnectionResult> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/integrations/test-connection`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Test connection failed");
  }
  return res.json();
}

export async function preSeedIntegrations(): Promise<IntegrationsResponse> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/integrations/pre-seed`, {
    method: "POST",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to pre-seed integrations");
  }
  return res.json();
}
