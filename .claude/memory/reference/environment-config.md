---
name: environment-config
description: Environment variables and configuration
type: reference
---

# Environment Configuration

## Required Variables (Backend)

### Database
- `DB_SERVER` - MySQL/MariaDB server hostname
- `DB_PORT` - Database port (default: 3306)
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password
- `DB_DB` - Database name
- Connection URI format: `mysql+asyncmy://user:password@server:port/database`

### Application
- `ENVIRONMENT` - Environment (local, production)
- `SECRET_KEY` - JWT secret key (regenerate for production)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time
- `FRONTEND_HOST` - Frontend URL for CORS and email links
- `BACKEND_CORS_ORIGINS` - CORS allowed origins (comma-separated)
- `PROJECT_NAME` - Project display name
- `STACK_NAME` - Docker stack name

### Email
- `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD` - SMTP credentials
- `EMAILS_FROM_EMAIL`, `EMAILS_FROM_NAME` - Sender info
- `EMAIL_TEST_USER` - Test email user
- `SMTP_TLS`, `SMTP_SSL`, `SMTP_PORT` - SMTP settings

### Auth & Security
- `JWT_AUDIENCE` - JWT audience claim (e.g., https://localhost:8000)
- `REFRESH_TOKEN_EXPIRE_DAYS` - Refresh token TTL (default: 30)
- `COOKIE_SECURE` - Enable secure cookies in production

### Stripe (Payments)
- `STRIPE_PUBLIC_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
- `STRIPE_CURRENCY` - Payment currency (e.g., "usd")

### Google OAuth
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` - Google OAuth credentials

### Integration Encryption
- `INTEGRATION_ENCRYPTION_KEY` - Fernet key for third-party credential encryption

### Docker
- `DOCKER_IMAGE_BACKEND`, `DOCKER_IMAGE_FRONTEND` - Docker image names
- `CERT_FILE`, `CERT_KEY` - SSL certificate paths
- `RSA_PUB_KEY`, `RSA_PRIVATE_KEY` - RSA key paths

## Frontend Variables (.env.local)

- `NEXT_PUBLIC_API_URL` - Backend API base URL
- `NEXT_PUBLIC_STRIPE_PUBLIC_KEY` - Stripe publishable key
- `NEXT_PUBLIC_STRIPE_WEBHOOK_SECRET` - Stripe webhook secret (if needed client-side)
- `NEXT_PUBLIC_STRIPE_CURRENCY` - Currency code
- `NEXT_PUBLIC_FEATURE_FLAG_DEFAULTS` - JSON array of enabled feature flags

## Configuration Files

### .env (local development)
Contains local development variables. Never commit to git.

### .env.local (frontend)
Frontend-specific environment overrides. Never commit to git.

### pyproject.toml (backend)
- Python version: >=3.12
- Dependencies defined here via Poetry
- Tool configurations (pytest, alembic, ruff, bandit)

## How to Apply

- Never commit .env or .env.local files
- Use environment variables for all sensitive data
- Set ENVIRONMENT to "local" or "production"
- Update BACKEND_CORS_ORIGINS when changing frontend URL
- Regenerate SECRET_KEY for production deployments
- Test database connection before deploying
