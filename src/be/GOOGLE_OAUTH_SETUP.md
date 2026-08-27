# Google OAuth 2.0 Setup Guide

This guide explains how to configure Google authentication for the Apostolic Faith Sacramento application.

## Prerequisites

- A Google Cloud Platform (GCP) account
- Access to the [Google Cloud Console](https://console.cloud.google.com/)

## Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click the project dropdown at the top and select "New Project"
3. Enter a project name (e.g., "Apostolic Faith Sacramento")
4. Click "Create"
5. Select your new project from the project dropdown

## Step 2: Enable Google+ API

1. In the left sidebar, go to **APIs & Services > Library**
2. Search for "Google+ API"
3. Click on it and press **Enable**

> Note: Even though the Google+ API is deprecated for new projects, it's still needed for the `google.auth` library to verify ID tokens. If you can't enable it, the code will work as long as you have OAuth 2.0 credentials configured.

## Step 3: Configure OAuth Consent Screen

1. Go to **APIs & Services > OAuth consent screen**
2. Choose **External** user type (unless you have a Google Workspace account)
3. Click **Create**
4. Fill in the required fields:
   - **App name**: Apostolic Faith Sacramento
   - **User support email**: Your support email (e.g., info@afcsacramento.org)
   - **Developer contact email**: Your email address
5. Add scopes if needed (the code requests `openid email profile` by default)
6. Click **Save and Continue**
7. Add test users (your email addresses) for development:
   - Go to **Users** section
   - Click **Add Users**
   - Add the email addresses that will test the login
8. Click **Save and Continue** (skip publishing for now)

## Step 4: Create OAuth 2.0 Credentials

1. Go to **APIs & Services > Credentials**
2. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
3. Select **Web application** as the application type
4. Fill in the details:

### For Development (Local)

- **Name**: AFC Local Development
- **Authorized JavaScript origins**:
  - `http://localhost:3000` (for local frontend dev)
- **Authorized redirect URIs**:
  - `http://localhost:8000/api/v1/google/auth/google` (or your backend URL)

### For Production

- **Name**: AFC Production
- **Authorized JavaScript origins**:
  - `https://your-domain.com`
- **Authorized redirect URIs**:
  - `https://your-backend-domain.com/api/v1/google/auth/google`

5. Click **Create**
6. **IMPORTANT**: Save the **Client ID** and **Client Secret** immediately - you'll need them for the environment variables

## Step 5: Configure Environment Variables

Add these to your `.env` file (or your deployment environment):

```bash
# Google OAuth credentials
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
```

### Production Deployment Notes

- **Never commit `.env` files** to version control
- Use your hosting provider's environment variable settings (Vercel, Railway, etc.)
- For Docker deployments, use a `.env.prod` file or pass via docker-compose

## Step 6: Verify the Setup

1. Start your backend and frontend
2. Navigate to `/login/` in your browser
3. Click "Sign in with Google"
4. You should be redirected to Google's login page
5. After successful authentication, you'll be redirected back and logged in

## Troubleshooting

### Error: "Google OAuth is not configured"

This error appears when `GOOGLE_CLIENT_ID` or `GOOGLE_CLIENT_SECRET` is missing or set to "dummy".

**Fix**: Check your environment variables are set correctly.

### Error: "Redirect URI mismatch"

Google rejects the redirect because it doesn't match what's configured in the Cloud Console.

**Fix**:
1. Go to **Credentials > OAuth 2.0 Client IDs**
2. Click on your client
3. Verify the redirect URI matches exactly: `{YOUR_API_BASE}/api/v1/google/auth/google`
4. Add any missing redirect URIs

### Error: "Google email not verified"

The user's Google account email is not verified.

**Fix**: The user needs to verify their email with Google. This is a Google-side issue, not a configuration problem.

### Users Can't Login Even With Valid Credentials

Check these:
1. **Database connection**: Ensure the backend can connect to MySQL
2. **User creation**: New users are auto-created on first login - check database for user records
3. **Cookie settings**: The redirect cookie uses `secure=True` and `samesite="lax"` - this works for localhost but may need adjustment for cross-domain production setups

### For Production Cross-Domain Cookies

If your frontend and backend are on different domains, update the cookie settings in `src/be/app/api/routes/google.py`:

```python
# Change from:
redirect = RedirectResponse(
    url=f"{settings.FRONTEND_HOST}/google-callback?scopes={scopes_param}",
    status_code=302,
)
redirect.set_cookie(
    key=settings.ACCESS_TOKEN_COOKIE_NAME,
    value=access_token,
    httponly=True,
    secure=True,          # Must be True for cross-site cookies
    samesite="none",      # Required for cross-site requests
    max_age=60 * int(settings.ACCESS_TOKEN_EXPIRE_MINUTES),
)
```

## How It Works

The Google OAuth flow in this application:

1. **Frontend**: User clicks "Sign in with Google" → generates PKCE challenge → redirects to `/google/login/google`
2. **Backend**: Generates code_verifier, stores in httpOnly cookie, redirects to Google's authorization page
3. **Google**: User logs in and grants permission → redirects back to `/auth/google` with authorization code
4. **Backend**:
   - Verifies PKCE using stored code_verifier
   - Exchanges code for ID token
   - Verifies ID token signature against Google's public keys
   - Finds or creates user in database
   - Issues JWT access/refresh tokens
   - Sets httpOnly cookies and redirects to frontend callback page
5. **Frontend**: Callback page verifies the session is valid, then redirects to home page

## Security Notes

- **PKCE (Proof Key for Code Exchange)**: Protects against authorization code interception attacks
- **httpOnly cookies**: Access tokens are stored in httpOnly cookies, preventing XSS theft
- **ID token verification**: The backend verifies Google's signature on the ID token before trusting the email
- **Auto-create users**: First-time Google users are automatically created in the database with `is_active=True` and `is_superuser=False`
- **Single-use code_verifier**: The PKCE verifier is stored in a cookie that expires after 5 minutes

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/google/login/google` | Start Google OAuth flow (redirects to Google) |
| GET | `/api/v1/google/auth/google` | Google callback handler (verifies token, issues JWT) |
| POST | `/api/v1/google/logout` | Revoke all user tokens (requires authentication) |

## Next Steps

After setting up Google OAuth:

1. Test with multiple Google accounts
2. Verify new users are created in the database
3. Check that JWT tokens are properly issued and cookies are set
4. For production, ensure HTTPS is enabled (required for secure cookies)
5. Consider adding rate limiting to the login endpoints if you expect high traffic
