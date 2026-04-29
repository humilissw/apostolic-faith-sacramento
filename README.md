# apostolic-faith-sacramento
Mono Repo for AFC Sacramento

# Generate an SSL-cert

## Linux/Mac OS

- Template:
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 3650 -nodes -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=CommonNameOrHostname"
```

- Example:
```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 3650 -nodes -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=localhost"
```

# Generates public and private keys for decrypting tokens
```bash
openssl genrsa -out private.pem 2048
```

```bash
openssl rsa -in private.pem -outform PEM -pubout -out public.pemowers
```

## Windows

1. Install Chocolatey.
2. Install mkcert.
3. Setup mkcert.

### Mkcert configuration

- Installing the root CA:
```pwsh
mkcert -install
```

- Select "Yes/OK" to install the root CA.

- Generate a self-signed certificate for localhost. Place this in infrastructure/certs.

```pwsh
mkcert -key-file key.pem -cert-file cert.pem example.com *.example.com localhost
```

# setup precommit

`pipx install pre-commit`

`pre-commit install`
