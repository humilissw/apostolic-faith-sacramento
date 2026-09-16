"""Phusion Passenger entrypoint for the AFC backend (src/be).

Passenger auto-detects ``passenger_wsgi.py`` and looks for a module-level
``application`` WSGI callable. All real wiring lives in ``wsgi.py``; this
file only re-exports it so the app can also be served from a different
project root.
"""

import os
import sys

_SERVICE_ROOT = os.path.dirname(os.path.abspath(__file__))
if _SERVICE_ROOT not in sys.path:
    sys.path.insert(0, _SERVICE_ROOT)

from wsgi import application  # noqa: E402,F401
