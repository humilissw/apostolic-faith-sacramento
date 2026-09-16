"""WSGI entrypoint for the AFC backend (src/be).

The app itself is ASGI (FastAPI); ``a2wsgi`` bridges it so classic WSGI
servers (Passenger, mod_wsgi, Waitress, gunicorn's WSGI workers, etc.) can
serve it. Import target for all WSGI hosts: ``wsgi:application``.

Run directly (after installing deps)::

    waitress-serve --port 5001 wsgi:application
"""

import os
import sys

# Ensure the service root is importable when a host loads this file by path
# (Passenger imports passenger_wsgi.py from an arbitrary cwd).
_SERVICE_ROOT = os.path.dirname(os.path.abspath(__file__))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)

from a2wsgi import ASGIMiddleware  # noqa: E402
from app.main import app as fastapi_app  # noqa: E402

#: The WSGI callable that hosts should serve.
application = ASGIMiddleware(fastapi_app)

# Convenience alias for hosts that look for a module-level ``app``.
app = application
