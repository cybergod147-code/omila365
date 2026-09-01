# app/utils/security.py
import base64
from cryptography.fernet import Fernet
from flask import current_app

def get_cipher():
    """Return a Fernet cipher using SECRET_KEY (padded to 32 bytes)."""
    key = current_app.config['SECRET_KEY']
    key = key.ljust(32)[:32]                     # ensure 32 bytes
    key_bytes = base64.urlsafe_b64encode(key.encode())
    return Fernet(key_bytes)

def encrypt_text(text):
    if not text:
        return None
    cipher = get_cipher()
    return cipher.encrypt(text.encode()).decode()

def decrypt_text(encrypted):
    if not encrypted:
        return None
    cipher = get_cipher()
    return cipher.decrypt(encrypted.encode()).decode()