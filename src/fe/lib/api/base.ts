// Single source of truth for where the SPA sends its requests.
//
// The frontend talks ONLY to the BFF (Flask, default https://localhost:8002),
// which owns auth server-side and proxies /api/v1/* to the FastAPI backend.
// The backend (port 8000) is never referenced from frontend code — there is
// deliberately no fallback to it here.
export const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://localhost:8002/";
export const API_V1 = "api/v1";
