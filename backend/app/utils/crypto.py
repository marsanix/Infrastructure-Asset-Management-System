"""
AES-256-GCM encryption untuk asset credentials.
Menggunakan Fernet (AES-128-CBC + HMAC) dari library cryptography
sebagai implementasi yang sudah battle-tested dan mudah digunakan.

Untuk kebutuhan AES-256-GCM murni, gunakan blok komentar di bawah.
"""
import os
import base64
from cryptography.fernet import Fernet
from flask import current_app


def _get_fernet() -> Fernet:
    """Ambil Fernet instance dari config."""
    key = current_app.config["AES_ENCRYPTION_KEY"]
    # Pastikan key valid base64 32-byte
    return Fernet(key.encode() if isinstance(key, str) else key)


def encrypt_text(plain_text: str) -> str:
    """Enkripsi string, return ciphertext sebagai string."""
    f = _get_fernet()
    return f.encrypt(plain_text.encode("utf-8")).decode("utf-8")


def decrypt_text(cipher_text: str) -> str:
    """Dekripsi ciphertext, return plaintext string."""
    f = _get_fernet()
    return f.decrypt(cipher_text.encode("utf-8")).decode("utf-8")


def generate_key() -> str:
    """Generate Fernet key baru — gunakan sekali untuk setup .env."""
    return Fernet.generate_key().decode("utf-8")
