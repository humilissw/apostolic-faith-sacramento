const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8000/";
const API_V1 = "api/v1";

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

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

export function getAuthToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("auth_token");
}

export function setAuthToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem("auth_token", token);
}

export function clearAuthToken(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem("auth_token");
}
