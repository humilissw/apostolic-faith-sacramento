from fastapi import APIRouter, Request
from authlib.integrations.starlette_client import OAuth

router = APIRouter(prefix="/google", tags=["health"])

oauth = OAuth()
oauth.register(
    name="google",
    client_id="dummy",
    client_secret="dummy",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


@router.get("/login/google")
async def login_via_google(request: Request):
    redirect_uri = request.url_for("auth_via_google")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google")
async def auth_via_google(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token["userinfo"]
    return dict(user)


# AUTH0_APP_NAME="afcwebapp"
# brew tap auth0/auth0-cli && brew install auth0 && auth0 login --no-input
# auth0 apps create -n "${AUTH0_APP_NAME}" -t regular \
#   -c http://localhost:8000/callback -l http://localhost:8000 \
#   -o http://localhost:8000 --reveal-secrets --json > app-details.json
# CLIENT_ID=$(python3 -c "import json; print(json.load(open('app-details.json'))['client_id'])")
# CLIENT_SECRET=$(python3 -c \
#   "import json; print(json.load(open('app-details.json'))['client_secret'])")
# DOMAIN=$(auth0 tenants list --json | python3 -c \
#   "import sys, json; print([t['name'] for t in json.load(sys.stdin) if t.get('active')][0])")
# SECRET=$(openssl rand -hex 64)
# echo "AUTH0_DOMAIN=${DOMAIN}" > .env && echo "AUTH0_CLIENT_ID=${CLIENT_ID}" >> .env
# echo "AUTH0_CLIENT_SECRET=${CLIENT_SECRET}" >> .env && echo "AUTH0_SECRET=${SECRET}" >> .env
# echo "AUTH0_REDIRECT_URI=http://localhost:8000/callback" >> .env
# rm app-details.json && echo ".env file created with your Auth0 details:" && cat .env
