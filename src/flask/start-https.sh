#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CERT_DIR="$SCRIPT_DIR/security_keys"

# Require certs
if [ ! -f "$CERT_DIR/cert.pem" ] || [ ! -f "$CERT_DIR/cert_key.pem" ]; then
    echo "ERROR: Missing certificate files in $CERT_DIR"
    echo "  Need: cert.pem, cert_key.pem"
    exit 1
fi

cd "$SCRIPT_DIR"

# Activate venv if not already active
if [ -z "${VIRTUAL_ENV:-}" ]; then
    VENV="$SCRIPT_DIR/.venv"
    if [ ! -f "$VENV/bin/activate" ]; then
        echo "No venv found at $VENV. Run: poetry install"
        exit 1
    fi
    . "$VENV/bin/activate"
fi

export FLASK_DEBUG=1

echo "Starting Flask over HTTPS"
echo "  Cert:   $CERT_DIR/cert.pem"
echo "  Key:    $CERT_DIR/cert_key.pem"
echo "  URL:    https://0.0.0.0:${PORT:-8000}"
echo ""

export CERT_PEM="$CERT_DIR/cert.pem"
export CERT_KEY="$CERT_DIR/cert_key.pem"

exec python -c "
import os, ssl
from wsgi import application
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain(os.environ['CERT_PEM'], os.environ['CERT_KEY'])
application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8000)), ssl_context=ssl_context)
"
