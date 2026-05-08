from cryptography.fernet import Fernet

key = Fernet.generate_key()
f = Fernet(key)
token = f.encrypt(b"enter something here")

decrypted = f.decrypt(token)

print(f"{key} \r\n")

print(f"{token} \r\n")

print(decrypted)
