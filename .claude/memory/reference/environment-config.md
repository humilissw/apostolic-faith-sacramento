---
name: environment-config
description: Environment variables and configuration
type: reference
---

# Environment Configuration

## Required Variables

### Database
- `DB_SERVER` - MySQL server hostname
- `DB_PORT` - MySQL server port (default: 3306)
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password
- `DB_DB` - Database name

### Application
- `ENVIRONMENT` - Environment (local, production)
- `SECRET_KEY` - JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration time
- `FRONTEND_HOST` - Frontend URL for CORS
- `BACKEND_CORS_ORIGINS` - CORS allowed origins

### Email
- `EMAIL_TEST_USER` - Test email user
- `EMAILS_FROM_EMAIL` - From email address
- `EMAILS_FROM_NAME` - From email name
- `SMTP_HOST` - SMTP server host
- `SMTP_PORT` - SMTP server port
- `SMTP_TLS` - Enable TLS
- `SMTP_SSL` - Enable SSL
- `emails_enabled` - Enable emails (boolean)

### Auth0 (optional)
- Auth0 configuration in auth0sample/

### Docker
- `DOCKER_IMAGE_BACKEND` - Docker image for backend
- `DOCKER_IMAGE_FRONTEND` - Docker image for frontend

## Configuration Files

### .env (local)
Contains local development variables

### .env.prod (production)
Contains production variables
- Never commit to git
- Use secrets management in production

### pyproject.toml
- Python version: >=3.13
- Dependencies defined here
- Tool configurations (pytest, alembic)

## Database URI Format

```
mysql+asyncmy://user:password@server:port/database
```

## How to Apply

- Never commit .env or .env.prod files
- Use environment variables for sensitive data
- Set ENVIRONMENT to "local" or "production"
- Update BACKEND_CORS_ORIGINS when changing frontend URL
- Regenerate SECRET_KEY for production deployments
- Test database connection before deploying
