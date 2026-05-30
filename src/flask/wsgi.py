from backend import create_app

application = create_app()

if __name__ == "__main__":
    application.run(ssl_context=("security_keys/cert.pem", "security_keys/cert_key.pem"))
