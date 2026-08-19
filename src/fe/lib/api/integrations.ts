const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";
const API_V1 = "api/v1";

import { fetchWithAuth } from "./auth";

// --- Integration types ---

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

// --- Integration API functions ---

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
