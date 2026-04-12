---
name: api-endpoints
description: API route documentation and patterns
type: reference
---

# API Endpoints

## Authentication

### POST /login/access-token
- Form data: username (email), password
- Returns: JWT access token
- Use for obtaining tokens

### POST /login/test-token
- Header: Authorization: Bearer <token>
- Returns: Current user info
- Use for testing tokens

### POST /password-recovery/{email}
- Generates password reset token and sends email
- Use for password recovery

### POST /reset-password/
- Body: token, new_password
- Resets password using token
- Use after user clicks reset link

## Users

### GET /users/
- Headers: Authorization: Bearer <token>
- Query: skip, limit
- Response: UsersPublic
- Requires: superuser

### POST /users/
- Headers: Authorization: Bearer <token>
- Body: UserCreate
- Response: UserPublic
- Requires: superuser

### PATCH /users/me
- Headers: Authorization: Bearer <token>
- Body: UserUpdateMe
- Response: UserPublic
- Updates current user's info

### PATCH /users/me/password
- Headers: Authorization: Bearer <token>
- Body: UpdatePassword (current_password, new_password)
- Response: Message
- Updates current user's password

### GET /users/me
- Headers: Authorization: Bearer <token>
- Response: UserPublic
- Gets current user

### DELETE /users/me
- Headers: Authorization: Bearer <token>
- Response: Message
- Deletes current user

### POST /users/signup
- No auth required
- Body: UserRegister
- Response: UserPublic
- Creates new user

## Items

### GET /items/
- Headers: Authorization: Bearer <token>
- Query: skip, limit
- Response: ItemsPublic
- Regular users: their items only
- Superusers: all items

### GET /items/{id}
- Headers: Authorization: Bearer <token>
- Response: ItemPublic
- Superuser or owner only

### POST /items/
- Headers: Authorization: Bearer <token>
- Body: ItemCreate
- Response: ItemPublic
- Creates item with owner_id from token

### PUT /items/{id}
- Headers: Authorization: Bearer <token>
- Body: ItemUpdate
- Response: ItemPublic
- Superuser or owner only

### DELETE /items/{id}
- Headers: Authorization: Bearer <token>
- Response: Message
- Superuser or owner only

## Members

### GET /members/
- Headers: Authorization: Bearer <token>
- Response: List of members
- TODO: Implement functionality

## Church Services

### GET /church-services/
- Headers: Authorization: Bearer <token>
- Response: List of services
- TODO: Implement functionality

### GET /church-services/{id}
- Headers: Authorization: Bearer <token>
- Response: ChurchService
- TODO: Implement functionality

## Video Uploads

### GET /video-uploads/
- Headers: Authorization: Bearer <token>
- Response: List of uploads
- TODO: Implement functionality

## Media

### GET /media/
- Headers: Authorization: Bearer <token>
- Response: List of media files
- TODO: Implement functionality

### POST /media/
- Headers: Authorization: Bearer <token>
- Body: VideoRequest
- Response: AddVideoResponse
- Adds new video upload

### GET /media/{media_name}
- Headers: Authorization: Bearer <token>
- Response: Media info
- TODO: Implement functionality

### PUT /media/
- TODO: Implement

### DELETE /media/
- TODO: Implement

## Announcements

### GET /announcements/
- Headers: Authorization: Bearer <token>
- Response: List of announcements
- TODO: Implement functionality

## Health Checks

### GET /health/
- Returns: {"is_healthy": true}
- Always available

### GET /health/liveness
- Returns: "Live"
- Kubernetes liveness probe

### GET /health/readiness
- Returns: "Ready"
- Kubernetes readiness probe

## Common Patterns

1. All routes require JWT token in Authorization header
2. Use `CurrentUser` dependency to get authenticated user
3. Check `current_user.is_superuser` for admin operations
4. Regular users only access their own resources
5. Use pydantic models for request/response validation
6. Return appropriate HTTPException with status codes
7. Include comprehensive docstrings
8. Use async functions for database operations

## How to Apply

- Check permission requirements before implementing routes
- Follow the patterns in existing routes (users.py, items.py)
- Use dependency injection for session and user
- Include proper error handling
- Add type hints to all functions