---
name: video-uploads page requires fetchWithAuth
description: video-uploads page must use fetchWithAuth not bare fetch, or it stays on Loading forever
type: feedback
---

Rule: Public-facing client pages that fetch from the backend must use `fetchWithAuth` (which sets `credentials: "include"`) instead of bare `fetch()`. Bare `fetch()` will not send cookies, which causes CORS preflight to fail against the HTTPS backend, and the page stays on "Loading..." indefinitely.

**Why:** The backend CORS config requires `allow_credentials=True`. Bare `fetch()` without `credentials: "include"` fails the CORS preflight, resulting in a blocked response that the page never handles.

**How to apply:** When building new public-facing pages that call the API, use `fetchWithAuth` from `@/lib/api` consistently. Do not use bare `fetch()` for API calls in client components.
