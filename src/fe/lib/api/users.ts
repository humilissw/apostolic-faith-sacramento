const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";
const API_V1 = "api/v1";

import { fetchWithAuth } from "./auth";

// --- User types ---

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

export interface CreateUserRequest {
  email: string;
  password: string;
  full_name?: string;
  is_active?: boolean;
  is_superuser?: boolean;
  scopes?: string[];
}

// --- User management API functions ---

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
