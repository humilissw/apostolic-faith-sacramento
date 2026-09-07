#!/usr/bin/env bash
#
# trust_dev_ca.sh - install the AFC dev root CA into the macOS trust store so
# browsers (Chrome/Safari) accept https://localhost:3000 / :8002 / :8000.
#
# Why a separate script: adding a root to the trust store is a machine-level,
# interactive step (sudo for the admin domain), kept out of
# generate_dev_certs.sh which must stay non-interactive and CI-safe.
#
# Strategy on macOS:
#   1) Prefer the ADMIN trust domain (System.keychain, needs sudo): every user
#      and all apps (Chrome, Safari, curl/SecureTransport) trust the CA.
#   2) If sudo isn't available non-interactively, fall back to the USER trust
#      domain (login keychain, no sudo). SecTrust - what Chrome/Safari consult
#      for the current user - honours this too.
#   3) Verify with `security verify-cert` and infrastructure/trustcheck.swift
#      (a browser-equivalent SecTrust evaluation against each live service).
#
# Idempotent: if the CA already verifies, nothing is re-added.
#
# Usage:
#   ./infrastructure/trust_dev_ca.sh [--clean-stale]
#     --clean-stale   also delete stale "localhost" certs from the login
#                     keychain (old self-signed leftovers that Chrome may pick
#                     instead of the CA chain). Prompts before deleting.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CA_PEM="${REPO_ROOT}/infrastructure/certs/ca.pem"
SYS_KC="/Library/Keychains/System.keychain"
LOGIN_KC="${HOME}/Library/Keychains/login.keychain-db"

[[ "$(uname -s)" == "Darwin" ]] || { echo "This script targets macOS (security/SecTrust)." >&2; exit 1; }

# Generate the CA if it doesn't exist yet (never regenerate an existing one).
if [[ ! -f "${CA_PEM}" ]]; then
    echo "CA not found - generating dev certs first..."
    "${REPO_ROOT}/infrastructure/generate_dev_certs.sh"
fi
[[ -f "${CA_PEM}" ]] || { echo "CA missing after generation: ${CA_PEM}" >&2; exit 1; }

already_trusted() { /usr/bin/security verify-cert -c "${CA_PEM}" -p ssl >/dev/null 2>&1; }

# Chromium browsers (Vivaldi/Chrome/Edge) on macOS IGNORE per-user trust
# settings - they only honour roots trusted in the ADMIN domain. So even when
# SecTrust/curl trust the CA from the login keychain, Vivaldi keeps failing
# until it's installed with `sudo ... -k System.keychain`.
in_system_kc() { security find-certificate -c "AFC Dev CA" "${SYS_KC}" >/dev/null 2>&1; }

install_to_admin() {
    echo "Adding CA to the ADMIN trust domain (${SYS_KC})..."
    sudo security add-trusted-cert -d -r trustRoot -p ssl -k "${SYS_KC}" "${CA_PEM}"
}

if already_trusted && in_system_kc; then
    echo "CA already trusted machine-wide (admin domain) - nothing to do."
elif already_trusted; then
    echo "CA is trusted for this user, but NOT in the admin domain."
    echo "Chromium browsers (Vivaldi/Chrome/Edge) only honour admin-domain roots."
    if [[ -t 0 ]]; then
        install_to_admin
    elif sudo -n true 2>/dev/null; then
        install_to_admin
    else
        echo "ERROR: admin install needs sudo with a password, and this run is"
        echo "       non-interactive. Run this script once in your own terminal:"
        echo "         ./infrastructure/trust_dev_ca.sh"
        exit 1
    fi
elif [[ -t 0 ]] && sudo -v 2>/dev/null; then
    install_to_admin
elif sudo -n true 2>/dev/null; then
    install_to_admin
else
    echo "sudo unavailable; adding to USER trust domain (login keychain)..."
    echo "  NOTE: SecTrust/curl/Safari will honour this, but Chromium browsers"
    echo "  (Vivaldi/Chrome/Edge) IGNORE per-user trust - they need the"
    echo "  admin-domain install below."
    # macOS may raise a GUI authorization prompt; cap the wait so this script
    # never hangs in non-interactive contexts (macOS has no coreutils timeout;
    # prefer `timeout`/`gtimeout` when present, else run without a cap).
    TIMEOUT_BIN=""
    command -v timeout  >/dev/null 2>&1 && TIMEOUT_BIN="timeout"
    if [[ -z "${TIMEOUT_BIN}" ]] && command -v gtimeout >/dev/null 2>&1; then TIMEOUT_BIN="gtimeout"; fi
    if ${TIMEOUT_BIN:+${TIMEOUT_BIN} 20} security add-trusted-cert -r trustRoot -p ssl "${CA_PEM}" 2>/dev/null; then
        echo "  user-domain trust added."
    else
        echo "  user-domain add failed or was cancelled (GUI auth prompt timed out)."
    fi
fi

if already_trusted; then
    echo "verify-cert: CA trusted (ssl policy)."
else
    echo "ERROR: CA still not trusted after install." >&2
    echo "Run this once in your own terminal and enter your password" >&2
    echo "(also REQUIRED for Vivaldi/Chrome, which ignore per-user trust):" >&2
    echo "  sudo security add-trusted-cert -d -r trustRoot -p ssl -k ${SYS_KC} ${CA_PEM}" >&2
    exit 1
fi

# Optional cleanup of stale self-signed "localhost" identities from earlier setups.
if [[ "${1:-}" == "--clean-stale" ]]; then
    n=$(security find-certificate -a -c localhost "${LOGIN_KC}" 2>/dev/null | grep -c '"alis"' || true)
    if [[ "${n}" -gt 0 ]]; then
        echo "Found ${n} 'localhost' certificate(s) in the login keychain."
        ans="n"
        [[ -t 0 ]] && read -r -p "Delete them? Old self-signed leftovers can shadow the CA chain. [y/N] " ans || true
        if [[ "${ans}" == "y" || "${ans}" == "Y" ]]; then
            security delete-certificate -c localhost "${LOGIN_KC}" && echo "deleted (repeat runs remove all copies)"
            while security find-certificate -a -c localhost "${LOGIN_KC}" >/dev/null 2>&1; do
                security delete-certificate -c localhost "${LOGIN_KC}" || break
            done
            echo "stale localhost certs removed."
        fi
    else
        echo "No stale 'localhost' certs in the login keychain."
    fi
fi

# Browser-equivalent verification against the live services, if they're up.
if [[ -f "${REPO_ROOT}/infrastructure/trustcheck.swift" ]] && command -v swift >/dev/null; then
    echo "SecTrust checks (what Chrome/Safari see) against live services:"
    ok_any=false
    for port in 3000 8002 8000; do
        if nc -z 127.0.0.1 "${port}" 2>/dev/null; then
            swift "${REPO_ROOT}/infrastructure/trustcheck.swift" "${port}" 2>/dev/null | grep "SecTrust" || true
            ok_any=true
        else
            echo "SecTrust: localhost:${port} => service not running (skipped)"
        fi
    done
    [[ "${ok_any}" == true ]] || echo "  (start the stack with docker-compose up -d to run these checks)"
fi

cat <<'EOF'

Done. If a browser still shows ERR_CERT_AUTHORITY_INVALID:
  1) Fully quit and relaunch the browser (Chrome caches trust state).
  2) Remove old "localhost" leftovers: rerun with --clean-stale, or open
      Keychain Access -> search "localhost" -> delete certificates/identities.
EOF
