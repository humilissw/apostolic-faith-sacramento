import os
from flask import Flask, redirect, render_template, request, url_for, g
from auth import auth0
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("AUTH0_SECRET")

# Configure session for Auth0
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)


@app.before_request
def store_request_response():
    """Make request/response available for Auth0 SDK"""
    g.store_options = {"request": request}


@app.route("/")
async def index():
    """Home page - shows login button or user profile"""
    user = await auth0.get_user(g.store_options)
    return render_template("index.html", user=user)


@app.route("/login")
async def login():
    """Redirect to Auth0 login"""
    authorization_url = await auth0.start_interactive_login({}, g.store_options)
    return redirect(authorization_url)


@app.route("/callback")
async def callback():
    """Handle Auth0 callback after login"""
    try:
        await auth0.complete_interactive_login(str(request.url), g.store_options)
        return redirect(url_for("index"))
    except Exception as e:
        return f"Authentication error: {str(e)}", 400


@app.route("/profile")
async def profile():
    """Protected route - shows user profile"""
    user = await auth0.get_user(g.store_options)

    if not user:
        return redirect(url_for("login"))

    return render_template("profile.html", user=user)


@app.route("/logout")
async def logout():
    """Logout and redirect to Auth0 logout"""
    # print(g.store_options)
    logout_url = await auth0.logout(store_options=g.store_options)
    print(logout_url)
    return redirect(logout_url)


if __name__ == "__main__":
    app.run(debug=True, port=8000)
