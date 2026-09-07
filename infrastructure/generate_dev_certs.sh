#!/usr/bin/env bash
#
# generate_dev_certs.sh - regenerate the TLS certificates used by every HTTPS
# container in the local docker-compose stack, signed by a local dev CA.
#
# Why a CA: browsers reject bare self-signed certs (ERR_CERT_AUTHORITY_INVALID)
# with no way to "accept" them for subresource requests. A local dev CA fixes
# that - install ca.pem ONCE into the system trust store and every leaf cert
# signed by it (localhost + docker DNS names) is trusted automatically.
#
# Layout:
#   infrastructure/certs/ca.pem          - dev root CA certificate
#   infrastructure/certs/ca_key.pem      - dev root CA private key
#   <project>/security_keys/cert.pem     - leaf cert for the service
#   <project>/security_keys/cert_key.pem - leaf private key
#   <project>/security_keys/key.pem      - alias copy of cert_key.pem (legacy)
#   <project>/security_keys/ca.pem       - copy of the CA (for in-container
#                                          verification, e.g. BFF BACKEND_CA_BUNDLE)
#
# SANs cover BOTH loopback and the docker-compose service DNS name (SANs never
# carry ports; the port only matters in the URL):
#   backend   src/be    https://localhost:8000  + https://backend:8000
#   bff       src/bff   https://localhost:8002  + https://bff:8002
#   frontend  src/fe    https://localhost:3000  + https://frontend:3000
# (health-edge :8001, database, adminer, mailcatcher serve plain HTTP - no certs.)
#
# These are DEVELOPMENT-ONLY certs, committed to the repo on purpose so a
# fresh clone runs out of the box. Production must use real certificates
# (future work: store as secrets).
#
# Usage:  ./infrastructure/generate_dev_certs.sh [--force]
#   --force   regenerate CA + certs even if they exist (default: skip existing)

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CA_DIR="${REPO_ROOT}/infrastructure/certs"
CA_PEM="${CA_DIR}/ca.pem"
CA_KEY="${CA_DIR}/ca_key.pem"
DAYS=3650
# Apple's SecTrust (Safari/Chrome on macOS) rejects TLS leaf certs valid for
# more than 825 days ("certificate is not standards compliant"). Keep leaves
# under that cap; the CA itself is exempt. Re-run this script yearly-ish.
LEAF_DAYS=820
FORCE=false
[[ "${1:-}" == "--force" ]] && FORCE=true

command -v openssl >/dev/null || { echo "openssl is required" >&2; exit 1; }

gen_ca() {
    if [[ "${FORCE}" == false && -f "${CA_PEM}" && -f "${CA_KEY}" ]]; then
        echo "skip   dev CA (exists; use --force to regenerate)"
        return
    fi
    mkdir -p "${CA_DIR}"
    openssl req -x509 -newkey rsa:4096 -sha256 -days "${DAYS}" -nodes \
        -keyout "${CA_KEY}" -out "${CA_PEM}" \
        -subj "/C=US/ST=California/L=Sacramento/O=Apostolic Faith Sacramento/OU=Development/CN=AFC Dev CA" \
        -addext "basicConstraints=critical,CA:TRUE" \
        -addext "keyUsage=critical,keyCertSign,cRLSign" \
        2>/dev/null
    chmod 600 "${CA_KEY}"
    echo "done   dev CA -> ${CA_PEM#"${REPO_ROOT}/"}"
}

gen_cert() {
    local project_dir="$1" service_dns="$2"

    local keys_dir="${REPO_ROOT}/${project_dir}/security_keys"
    mkdir -p "${keys_dir}"

    if [[ "${FORCE}" == false && -f "${keys_dir}/cert.pem" && -f "${keys_dir}/cert_key.pem" ]]; then
        echo "skip   ${project_dir}/security_keys (exists; use --force to regenerate)"
        cp "${CA_PEM}" "${keys_dir}/ca.pem"
        return
    fi

    # SANs: loopback + docker DNS name + host.docker.internal so the cert is
    # valid as https://localhost:<port> AND https://<service>:<port>.
    local san="DNS:localhost,DNS:${service_dns},DNS:host.docker.internal,IP:127.0.0.1"

    # Prefer real OpenSSL (homebrew) if present; fall back to whatever is on
    # PATH. Extension config goes through -extfile so LibreSSL works too.
    local OPENSSL="openssl"
    [[ -x /opt/homebrew/opt/openssl@3/bin/openssl ]] && OPENSSL="/opt/homebrew/opt/openssl@3/bin/openssl"

    local ext_file; ext_file="$(mktemp)"
    cat > "${ext_file}" <<EOF
subjectAltName=${san}
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
EOF

    "${OPENSSL}" req -newkey rsa:4096 -nodes \
        -keyout "${keys_dir}/cert_key.pem" \
        -out "${keys_dir}/cert.csr" \
        -subj "/C=US/ST=California/L=Sacramento/O=Apostolic Faith Sacramento/OU=Development/CN=localhost" \
        2>/dev/null

    "${OPENSSL}" x509 -req -in "${keys_dir}/cert.csr" \
        -CA "${CA_PEM}" -CAkey "${CA_KEY}" -CAcreateserial \
        -out "${keys_dir}/cert.pem" -days "${LEAF_DAYS}" -sha256 \
        -extfile "${ext_file}"

    rm -f "${keys_dir}/cert.csr" "${CA_PEM}.srl" "${CA_DIR}/ca.srl" "${ext_file}"
    cp "${keys_dir}/cert_key.pem" "${keys_dir}/key.pem"   # legacy alias
    cp "${CA_PEM}" "${keys_dir}/ca.pem"                   # in-container verifier
    # cert.pem = leaf + CA chain, so every server (uvicorn/werkzeug/next)
    # presents the full chain and browsers can build it to the trusted dev CA.
    cat "${keys_dir}/cert.pem" "${CA_PEM}" > "${keys_dir}/cert.chain.tmp"
    mv "${keys_dir}/cert.chain.tmp" "${keys_dir}/cert.pem"
    chmod 600 "${keys_dir}/cert_key.pem" "${keys_dir}/key.pem"

    echo "done   ${project_dir}/security_keys  (${san})"
}

echo "Generating dev CA + TLS certs for the docker stack..."
gen_ca
gen_cert "src/be" "backend"
gen_cert "src/bff" "bff"
gen_cert "src/fe" "frontend"

cat <<'EOF'

Done. Next steps:
  1) Trust the dev CA ONCE (macOS, then restart Chrome):
      sudo security add-trusted-cert -d -r trustRoot \
        -k /Library/Keychains/System.keychain infrastructure/certs/ca.pem
  2) Rebuild containers to pick up new certs:
      docker-compose build && docker-compose up -d

EOF
