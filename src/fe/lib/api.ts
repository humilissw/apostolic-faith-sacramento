import { API_BASE, API_V1 } from "./api/base";

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

// --- Auth state detection (cookies are the source of truth) ---

function hasAuthCookie(): boolean {
  return document.cookie.includes("access_token=");
}

// --- Login API ---

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

// --- Check if user is authenticated ---

export function isAuthenticated(): boolean {
  return hasAuthCookie();
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
    credentials: "include",
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
    credentials: "include",
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

// --- User management API ---

export interface UserWithScopes {
  email: string;
  is_active: boolean;
  id: string;
  new_id: string;
  full_name: string | null;
  assigned_scopes: string[];
}

export interface UsersWithScopesResponse {
  data: UserWithScopes[];
  count: number;
}

export async function fetchUsersWithScopes(skip: number = 0, limit: number = 50): Promise<UsersWithScopesResponse> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/users/?skip=${skip}&limit=${limit}`);
  if (!res.ok) {
    throw new Error("Failed to fetch users");
  }
  const body = await res.json();
  return body as UsersWithScopesResponse;
}

export async function fetchAllUsers(): Promise<UsersWithScopesResponse> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/users/admin/all`);
  if (!res.ok) {
    throw new Error("Failed to fetch all users");
  }
  const body = await res.json();
  return body as UsersWithScopesResponse;
}

export async function setUserScopes(userId: string, scopes: string[]): Promise<string[]> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/users/admin/${userId}/scopes`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(scopes),
    },
  );
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to set user scopes");
  }
  return res.json();
}

export async function deleteUser(userId: string): Promise<void> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/users/${userId}`,
    {
      method: "DELETE",
    },
  );
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to delete user");
  }
}

export async function deleteUsers(userIds: string[]): Promise<void> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/users/admin/bulk-delete`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(userIds),
    },
  );
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to delete users");
  }
}

/**
 * Send password reset emails to one or more users (admin only).
 * Each user receives an HMAC-signed, single-use link to set a new password.
 */
export async function bulkAdminPasswordReset(
  userIds: string[],
): Promise<{ message: string }> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/admin/password-reset/bulk`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_ids: userIds }),
    },
  );
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to send password reset emails");
  }
  return res.json();
}

/** Send a password reset email to a single user (admin only). */
export async function sendPasswordReset(userId: string): Promise<{ message: string }> {
  return bulkAdminPasswordReset([userId]);
}

export interface CreateUserRequest {
  email: string;
  // No password: admins must never set a user's password. The new user
  // receives an email with an HMAC-signed, single-use set-password link.
  full_name?: string;
  is_active?: boolean;
  is_superuser?: boolean;
  scopes?: string[];
}

export async function createUser(data: CreateUserRequest): Promise<UserWithScopes> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/users/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    },
  );
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to create user");
  }
  return res.json();
}

// --- Video upload admin API ---

export interface VideoUploadAdmin {
  id: string;
  upload_location: string;
  upload_name: string;
  media_association_date: string;
  speaker_name: string | null;
  reference_text: string | null;
  description: string | null;
  owner_id: string;
  created_on: string;
  updated_on: string | null;
}

export async function patchVideoUpload(
  id: string,
  data: Partial<VideoUploadAdmin>,
): Promise<VideoUploadAdmin> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/video-uploads/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to update video upload");
  }
  return res.json();
}

export async function createVideoUpload(data: Partial<VideoUploadAdmin>): Promise<VideoUploadAdmin> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/video-uploads/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to create video upload");
  }
  return res.json();
}

export async function deleteVideoUpload(id: string): Promise<void> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/video-uploads/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to delete video upload");
  }
}

// --- All video uploads (for admin) ---

export async function fetchAllVideoUploads(): Promise<{ data: VideoUploadAdmin[]; count: number }> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/video-uploads/`);
  if (!res.ok) {
    throw new Error("Failed to fetch video uploads");
  }
  const body = await res.json();
  return body;
}

// --- Scheduler API functions ---

export interface Assignment {
  id: string;
  user_id: string;
  user_email: string;
  user_full_name: string | null;
  event_date: string;
  type: "music" | "service";
  role: string;
  instrument: string | null;
  notes: string | null;
  group_leader: boolean;
  created_on: string;
  updated_on: string | null;
}

export interface AssignmentConflict {
  id: string;
  type: string;
  role: string;
  event_date: string;
}

export interface AssignmentCreateInput {
  user_id: string;
  event_date: string;
  type: "music" | "service";
  role?: string;
  instrument?: string | null;
  notes?: string | null;
}

export interface AssignmentUpdateInput {
  event_date?: string;
  type?: "music" | "service";
  role?: string;
  instrument?: string | null;
  notes?: string | null;
  user_id?: string;
}

export interface BulkAssignEntry {
  user_id: string;
  role: string;
  instrument: string | null;
  notes: string | null;
  group_leader: boolean;
}

export interface BulkAssignRequest {
  event_date: string;
  type: "music" | "service";
  entries: BulkAssignEntry[];
}

export interface BulkAssignConflict {
  user_id: string;
  message: string;
  conflicts?: AssignmentConflict[];
}

export interface BulkAssignResponse {
  created: Assignment[];
  conflicts: BulkAssignConflict[];
}

export interface AssignmentsResponse {
  data: Assignment[];
  count: number;
}

export async function fetchAssignments(): Promise<AssignmentsResponse> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/`);
  if (!res.ok) {
    throw new Error("Failed to fetch assignments");
  }
  return res.json();
}

export async function fetchAssignment(id: string): Promise<Assignment> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/${id}`);
  if (!res.ok) {
    throw new Error("Failed to fetch assignment");
  }
  return res.json();
}

export async function createAssignment(data: AssignmentCreateInput): Promise<Assignment> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    if (res.status === 409) {
      const detail = JSON.parse(body);
      throw new Error(detail.detail?.message || detail.detail || "Conflict: user already has an assignment on this date.");
    }
    throw new Error(body || "Failed to create assignment");
  }
  return res.json();
}

export async function updateAssignment(id: string, data: AssignmentUpdateInput): Promise<Assignment> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to update assignment");
  }
  return res.json();
}

export async function deleteAssignment(id: string): Promise<void> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to delete assignment");
  }
}

export async function bulkAssignAssignments(data: BulkAssignRequest): Promise<BulkAssignResponse> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/bulk`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to bulk assign assignments");
  }
  return res.json();
}

export async function fetchMyAssignments(): Promise<AssignmentsResponse> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/my-assignments`);
  if (!res.ok) {
    throw new Error("Failed to fetch my assignments");
  }
  return res.json();
}

export async function fetchCalendarAssignments(startDate: string, endDate: string): Promise<AssignmentsResponse> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/scheduler/calendar?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`
  );
  if (!res.ok) {
    throw new Error("Failed to fetch calendar assignments");
  }
  return res.json();
}

export async function fetchCalendarWithNames(startDate: string, endDate: string): Promise<AssignmentsResponse> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/scheduler/calendar-with-names?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`
  );
  if (!res.ok) {
    throw new Error("Failed to fetch calendar with names");
  }
  return res.json();
}

export async function fetchMyCalendar(startDate: string, endDate: string): Promise<AssignmentsResponse> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/scheduler/my-calendar?start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`
  );
  if (!res.ok) {
    throw new Error("Failed to fetch my calendar");
  }
  return res.json();
}

// --- Time-off request API ---

export interface TimeOffRequest {
  id: string;
  user_id: string;
  date: string;
  status: "pending" | "approved" | "declined";
  notes: string | null;
  created_on: string;
  updated_on: string | null;
}

export interface TimeOffRequestsResponse {
  data: TimeOffRequest[];
  count: number;
}

export async function createTimeOffRequest(data: { date: string; notes?: string | null }): Promise<TimeOffRequest> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/time-off-request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to create time-off request");
  }
  return res.json();
}

export async function fetchMyTimeOffRequests(): Promise<TimeOffRequestsResponse> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/scheduler/time-off-requests`);
  if (!res.ok) {
    throw new Error("Failed to fetch time-off requests");
  }
  return res.json();
}

export async function approveTimeOffRequest(timeOffId: string): Promise<void> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/scheduler/time-off-requests/${timeOffId}/approve`,
    { method: "PATCH" }
  );
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to approve time-off request");
  }
}

export async function declineTimeOffRequest(timeOffId: string): Promise<void> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/scheduler/time-off-requests/${timeOffId}/decline`,
    { method: "PATCH" }
  );
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to decline time-off request");
  }
}

export async function deleteTimeOffRequest(timeOffId: string): Promise<void> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/scheduler/time-off-requests/${timeOffId}`,
    { method: "DELETE" }
  );
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to delete time-off request");
  }
}

export async function fetchTimeOffByDateRange(start: string, end: string): Promise<TimeOffRequestsResponse> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/scheduler/time-off-requests?start_date=${encodeURIComponent(start)}&end_date=${encodeURIComponent(end)}`
  );
  if (!res.ok) {
    throw new Error("Failed to fetch time-off requests");
  }
  return res.json();
}

// --- Feature flag API functions ---

export interface FeatureFlagEntry {
  id: string;
  name: string;
  description: string;
  is_enabled: boolean;
  created_on: string;
  updated_on: string | null;
}

export interface FeatureFlagsResponse {
  data: FeatureFlagEntry[];
  count: number;
}

export async function fetchFeatureFlags(): Promise<FeatureFlagsResponse> {
  // Must carry the session cookie (endpoint is superuser-only); a bare
  // fetch() drops cookies cross-origin. See feature-flag-context.
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/feature-flags/`);
  if (!res.ok) {
    throw new Error("Failed to fetch feature flags");
  }
  return res.json();
}

export async function updateFeatureFlag(name: string, enabled: boolean): Promise<FeatureFlagEntry> {
  const res = await fetchWithAuth(
    `${API_BASE}${API_V1}/feature-flags/${name}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ is_enabled: enabled }),
    },
  );
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to update feature flag");
  }
  return res.json();
}

export async function preSeedFeatureFlags(): Promise<FeatureFlagsResponse> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/feature-flags/pre-seed`, {
    method: "POST",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to pre-seed feature flags");
  }
  return res.json();
}


// --- Events API functions ---

export interface Event {
  id: string;
  title: string;
  description: string | null;
  date: string;
  start_time: string;
  end_time: string;
  created_on: string;
  updated_on: string | null;
  flyer_url: string | null;
}

export interface EventCreateInput {
  title: string;
  description: string | null;
  date: string;
  start_time: string;
  end_time: string;
}

export interface EventUpdateInput {
  title?: string;
  description?: string | null;
  date?: string;
  start_time?: string;
  end_time?: string;
}

export interface EventsResponse {
  data: Event[];
  count: number;
}

export async function fetchEvents(): Promise<EventsResponse> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/events/`);
  if (!res.ok) {
    throw new Error("Failed to fetch events");
  }
  return res.json();
}

export async function fetchEvent(id: string): Promise<Event> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/events/${id}`);
  if (!res.ok) {
    throw new Error("Failed to fetch event");
  }
  return res.json();
}

export async function createEvent(data: EventCreateInput): Promise<Event> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/events/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to create event");
  }
  return res.json();
}

export async function updateEvent(id: string, data: EventUpdateInput): Promise<Event> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/events/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to update event");
  }
  return res.json();
}

export async function deleteEvent(id: string): Promise<void> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/events/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to delete event");
  }
}

// Delete multiple events in a single request.
export async function deleteEvents(ids: string[]): Promise<void> {
  if (ids.length === 0) return;
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/events/bulk`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ event_ids: ids }),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to delete events");
  }
}

// Events are stored/displayed in the church's local timezone.
export const EVENT_TIME_ZONE = "America/Los_Angeles";

// The backend serialises datetimes without a zone suffix (they are UTC
// wall-clock: the dialog converts entered Pacific wall-clock times to UTC ISO
// before saving). Attach "Z" so they parse as the instant they represent;
// always *format* them in EVENT_TIME_ZONE so what admins typed round-trips.
export function parseServerDate(value: string): Date {
  const parsed = /Z|[+-]\d{2}:\d{2}$/.test(value) ? new Date(value) : new Date(`${value}Z`);
  return Number.isNaN(parsed.getTime()) ? new Date(NaN) : parsed;
}

// "yyyy-MM-dd" calendar-day key for an instant, viewed in EVENT_TIME_ZONE.
function dayKeyInZone(date: Date): string {
  return new Intl.DateTimeFormat("en-CA", {
    timeZone: EVENT_TIME_ZONE,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(date);
}

// True when an event's start and end fall on different calendar days
// (i.e. it spans a range of days).
export function isMultiDayEvent(event: { start_time: string; end_time: string }): boolean {
  return dayKeyInZone(parseServerDate(event.start_time)) !== dayKeyInZone(parseServerDate(event.end_time));
}

// Every calendar day ("yyyy-MM-dd" in EVENT_TIME_ZONE) an event occupies,
// from its start day through its end day inclusive. Multi-day events appear
// on the calendar for each of these days.
export function eventCalendarDays(event: { start_time: string; end_time: string }): string[] {
  const start = parseServerDate(event.start_time);
  const end = parseServerDate(event.end_time);
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return [];
  const startKey = dayKeyInZone(start);
  const endKey = dayKeyInZone(end);
  if (endKey <= startKey) return [startKey];
  const [year, month, day] = startKey.split("-").map(Number);
  const days = [startKey];
  // Noon UTC is the same calendar day everywhere in US timezones, so stepping
  // whole days from noon never skips or duplicates a day across DST changes.
  for (let i = 1; i <= 366; i++) {
    const key = dayKeyInZone(new Date(Date.UTC(year, month - 1, day + i, 12)));
    days.push(key);
    if (key >= endKey) break;
  }
  return days;
}

// Human-friendly date label; shows a range ("05 Sep - 08 Sep") for events
// that span multiple days, and a single date otherwise.
export function formatEventDateRange(event: { date: string; start_time: string; end_time: string }): string {
  const opts: Intl.DateTimeFormatOptions = { day: "2-digit", month: "short", timeZone: EVENT_TIME_ZONE };
  const startLabel = parseServerDate(event.date).toLocaleDateString("en-US", opts);
  if (!isMultiDayEvent(event)) return startLabel;
  const endLabel = parseServerDate(event.end_time).toLocaleDateString("en-US", opts);
  return `${startLabel} - ${endLabel}`;
}

// "6:30 AM"-style time label for an event timestamp, in EVENT_TIME_ZONE.
export function formatEventTime(value: string): string {
  return parseServerDate(value).toLocaleTimeString("en-US", {
    timeZone: EVENT_TIME_ZONE,
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

// Resolve a backend-relative flyer URL (Event.flyer_url) to an absolute URL.
export function flyerImageUrl(flyerUrl: string | null): string | null {
  if (!flyerUrl) return null;
  const base = API_BASE.endsWith("/") ? API_BASE.slice(0, -1) : API_BASE;
  return `${base}${flyerUrl.startsWith("/") ? "" : "/"}${flyerUrl}`;
}

export async function uploadEventFlyer(id: string, file: File): Promise<Event> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/events/${id}/flyer`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to upload flyer");
  }
  return res.json();
}

export async function deleteEventFlyer(id: string): Promise<void> {
  const res = await fetchWithAuth(`${API_BASE}${API_V1}/events/${id}/flyer`, {
    method: "DELETE",
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || "Failed to delete flyer");
  }
}
