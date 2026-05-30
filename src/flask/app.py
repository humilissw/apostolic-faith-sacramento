import os

from backend import create_app

MyApp = create_app()

if __name__ == "__main__":
    MyApp.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)  # nosec B104
