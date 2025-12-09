# apostolic-faith-sacramento
Mono Repo for AFC Sacramento 

# Generate an SSL-cert

## Linux/Mac OS

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -sha256 -days 3650 -nodes -subj "/C=XX/ST=StateName/L=CityName/O=CompanyName/OU=CompanySectionName/CN=CommonNameOrHostname"
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

- Generate a self-signed certificate for localhost.

```pwsh
mkcert -key-file key.pem -cert-file cert.pem example.com *.example.com localhost
```