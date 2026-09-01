const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";
const API_V1 = "api/v1";

import { fetchWithAuth } from "./auth";

// --- Feature flag types ---

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

// --- Feature flag API functions ---

export async function fetchFeatureFlags(): Promise<FeatureFlagsResponse> {
  const res = await fetch(`${API_BASE}${API_V1}/feature-flags/`);
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
