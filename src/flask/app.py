import os

from app import create_app

application = create_app()

if __name__ == "__main__":

    app = application
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)  # nosec B104
