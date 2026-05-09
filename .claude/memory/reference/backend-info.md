---
name: Backend runs HTTPS on localhost:8000
description: Backend server runs on https://localhost:8000, health endpoint at /api/v1/health/
type: reference
---

Fact: Backend runs over HTTPS at https://localhost:8000 (not HTTP).

Health check endpoint: `https://localhost:8000/api/v1/health/` — returns `"Healthy"` as plain text.

When debugging frontend API issues, verify backend is reachable first:
```
curl -sk https://localhost:8000/api/v1/health/
```

All frontend API URLs must use `https://` for localhost in production deployment. In `.env` files, `NEXT_PUBLIC_API_URL=https://localhost:8000/`.
