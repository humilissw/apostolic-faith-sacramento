"""WSGI entrypoint for the AFC BFF (src/bff).

The BFF is a plain Flask app, so it is already WSGI-native — no bridge
needed. Import target for all WSGI hosts: ``wsgi:application``.

Run directly (after installing deps)::

    waitress-serve --port 8002 wsgi:application
"""

import os
import sys

# Ensure the service root is importable when a host loads this file by path
# (Passenger imports passenger_wsgi.py from an arbitrary cwd).
_SERVICE_ROOT = os.path.dirname(os.path.abspath(__file__))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)

from app.app import app as flask_app  # noqa: E402

#: The WSGI callable that hosts should serve.
application = flask_app

# Convenience alias for hosts that look for a module-level ``app``.
app = application
