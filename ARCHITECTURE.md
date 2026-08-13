# Apostolic Faith Sacramento - Architecture Documentation

## System Overview

A three-tier web application for Apostolic Faith Sacramento church, built with a FastAPI backend, Next.js frontend, and planned mobile client. All communication is via RESTful JSON over HTTPS.

## Architecture Diagram

See [erDiagram.mmd](./erDiagram.mmd) for the entity-relationship diagram of core database entities.

## Technology Stack

### Backend (`src/be/`)
- **Framework**: FastAPI (Python 3.13+)
- **ORM**: SQLModel (Pydantic + SQLAlchemy 2.0)
- **Database**: MySQL (asyncmy driver)
- **Migrations**: Alembic
- **Auth**: JWT (access + refresh tokens), OAuth2 Authorization Code Flow with PKCE
- **Password Hashing**: bcrypt

### Frontend (`src/fe/`)
- **Framework**: Next.js 16 (App Router, React 19)
- **Language**: TypeScript 5.9+ (strict mode)
- **Styling**: Tailwind CSS v4
- **Components**: HeroUI + shadcn/ui (Radix UI primitives)
- **Build**: Static export to `out/`
- **Package Manager**: bun

### Infrastructure
- **SSL**: Self-signed or mkcert certificates in `infrastructure/certs/`
- **Encryption**: Fernet-based credential encryption for third-party integrations
- **Container**: Docker Compose for local development

## Application Structure

```
apostolic-faith-sacramento/
├── src/
│   ├── be/                          # Backend (FastAPI)
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   ├── deps.py          # Dependency injection (session, auth)
│   │   │   │   ├── main.py          # Router assembly
│   │   │   │   └── routes/          # API route modules
│   │   │   ├── core/
│   │   │   │   ├── db.py            # Async session configuration
│   │   │   │   ├── security.py      # JWT, password hashing
│   │   │   │   ├── rate_limiter.py  # Rate limiting middleware
│   │   │   │   ├── result.py        # Unified result pattern
│   │   │   │   └── scopes.py        # Permission scope definitions
│   │   │   ├── services/            # Business logic layer
│   │   │   ├── repositories/        # Data access layer
│   │   │   ├── models.py            # SQLModel database models
│   │   │   ├── crud.py              # Generic CRUD operations
│   │   │   └── config.py            # Pydantic-settings configuration
│   │   ├── alembic/                 # Database migrations
│   │   └── tests/                   # Pytest tests
│   ├── fe/                          # Frontend (Next.js)
│   │   ├── app/
│   │   │   ├── (auth)/              # Auth page group (login)
│   │   │   ├── (main)/              # Public pages
│   │   │   │   ├── sermon/
│   │   │   │   ├── media/
│   │   │   │   ├── live-service/
│   │   │   │   ├── contact/
│   │   │   │   ├── doctrines/
│   │   │   │   ├── donate/
│   │   │   │   ├── integrations/
│   │   │   │   ├── users-admin/
│   │   │   │   ├── video-uploads/
│   │   │   │   └── video-uploads-admin/
│   │   │   ├── (media)/
│   │   │   │   └── upload-videos/   # Media upload flow
│   │   │   └── layout.tsx           # Root layout + providers
│   │   ├── components/              # Reusable UI components
│   │   ├── hooks/                   # Custom React hooks
│   │   └── lib/                     # Utility functions
│   └── mobile/                      # Mobile app (planned)
├── infrastructure/
│   ├── certs/                       # SSL certificates
│   ├── db/                          # Database config
│   └── security_keys/              # Encryption keys
└── erDiagram.mmd                   # Database entity diagram
```

## API Endpoints

| Module | Routes | Description |
|--------|--------|-------------|
| `users.py` | `/api/users` | CRUD for users (admin) |
| `user_scopes.py` | `/api/user-scopes` | User permission scopes |
| `login.py` | `/api/auth` | Login, logout, token operations |
| `private.py` | `/api/private` | Private/user-specific endpoints |
| `media.py` | `/api/media` | Media management |
| `video_uploads.py` | `/api/video-uploads` | Video upload lifecycle |
| `members.py` | `/api/members` | Church member management |
| `church_services.py` | `/api/church-services` | Service management |
| `announcements.py` | `/api/announcements` | Church announcements |
| `payments.py` | `/api/payments` | Donations and payment processing |
| `integrations.py` | `/api/integrations` | Third-party integration config |
| `client_credentials.py` | `/api/client-credentials` | OAuth2 client management |
| `google.py` | `/api/google` | Google integration (OAuth callback) |
| `items.py` | `/api/items` | Generic item management |
| `health.py` | `/api/health` | Health check endpoint |

## Design Patterns

### Backend Patterns

1. **Layered Architecture**: Routes -> Services -> Repositories -> DB
2. **SQLModel Pattern**: Base model (shared fields) -> Create/Update models -> Table model -> Public response model
3. **Dependency Injection**: FastAPI `Depends()` for session, current user, auth checks
4. **Async-First**: All DB operations use `await session.execute()`
5. **UUID Primary Keys**: All entities use UUID4 for IDs; `new_id` alias for convenience
6. **Result Pattern**: Unified response types in `core/result.py`
7. **Pydantic Settings**: Configuration via `config.py` with environment variable validation

### Frontend Patterns

1. **App Router**: Route groups `(auth)`, `(main)`, `(media)` for layout sharing
2. **Server Components**: Default to server components; `"use client"` only when needed
3. **Static Export**: Build outputs to `out/` for simple deployment
4. **shadcn/ui Primitives**: Radix-based components with HeroUI for specialized widgets
5. **Utility-first**: `cn()` from `@/lib/utils` for class merging

## Database Entities

See [erDiagram.mmd](./erDiagram.mmd) for the complete entity-relationship diagram.

### Core Domain Tables

| Table | Purpose |
|-------|---------|
| `users` | Application users with email, role, and auth state |
| `user_scopes` | User-permission mappings |
| `members` | Church member records |
| `church_services` | Scheduled church services |
| `media` | Uploaded media assets |
| `video_uploads` | Video upload task tracking |
| `payments` | Donation/payment records (Stripe-integrated) |
| `donation_configs` | Preset donation amounts/frequencies |
| `announcements` | Church-wide announcements |
| `integration_configs` | Third-party service configurations |
| `client_credentials` | OAuth2 client credentials |
| `authorization_codes` | OAuth2 auth code flow with PKCE |
| `refresh_tokens` | JWT refresh token storage |
| `items` | Generic item tracking (legacy/utility) |

## Authentication Flow

1. **Login**: Username/password -> access token + refresh token
2. **API Access**: Bearer JWT in `Authorization` header
3. **Token Refresh**: Refresh token -> new access token
4. **OAuth2 PKCE**: Authorization code flow for third-party services
5. **Scopes**: Fine-grained permissions via `user_scopes` table
6. **Service Auth**: Client credentials for service-to-service communication

## Security Considerations

- Passwords hashed with bcrypt
- Credentials encrypted with Fernet for third-party integrations
- SSL/TLS required for all production traffic
- `.env` files never committed (gitignore)
- Restricted API keys for Stripe and Google services
- Rate limiting via `core/rate_limiter.py`
