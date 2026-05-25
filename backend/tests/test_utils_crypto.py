"""
Unit tests: crypto.py
Enkripsi AES-256 Fernet untuk asset credentials.
"""
import pytest
from cryptography.fernet import Fernet


class TestCrypto:
    """Test encrypt/decrypt dengan app context."""

    def test_encrypt_returns_different_from_plaintext(self, app):
        with app.app_context():
            from app.utils.crypto import encrypt_text
            plain = "s3cr3t_p@ssword"
            cipher = encrypt_text(plain)
            assert cipher != plain
            assert len(cipher) > 0

    def test_decrypt_returns_original_text(self, app):
        with app.app_context():
            from app.utils.crypto import encrypt_text, decrypt_text
            plain = "router_admin_password123!"
            cipher = encrypt_text(plain)
            decrypted = decrypt_text(cipher)
            assert decrypted == plain

    def test_each_encryption_produces_unique_ciphertext(self, app):
        """Fernet menggunakan IV acak — dua enkripsi plain yang sama → ciphertext berbeda."""
        with app.app_context():
            from app.utils.crypto import encrypt_text
            plain = "same_password"
            cipher1 = encrypt_text(plain)
            cipher2 = encrypt_text(plain)
            assert cipher1 != cipher2  # IV berbeda tiap encrypt

    def test_decrypt_wrong_key_raises(self):
        """Ciphertext dari key berbeda tidak bisa didekripsi."""
        wrong_key = Fernet.generate_key().decode()
        f = Fernet(wrong_key)
        ciphertext = f.encrypt(b"secret").decode()

        import os
        os.environ["AES_ENCRYPTION_KEY"] = Fernet.generate_key().decode()

        # Re-import dengan key baru — pakai app context baru
        from app import create_app
        new_app = create_app("testing")
        new_app.config["AES_ENCRYPTION_KEY"] = Fernet.generate_key().decode()

        with new_app.app_context():
            from app.utils.crypto import decrypt_text
            from cryptography.fernet import InvalidToken
            with pytest.raises(InvalidToken):
                decrypt_text(ciphertext)

    def test_encrypt_empty_string(self, app):
        with app.app_context():
            from app.utils.crypto import encrypt_text, decrypt_text
            plain = ""
            cipher = encrypt_text(plain)
            assert decrypt_text(cipher) == plain

    def test_encrypt_unicode(self, app):
        with app.app_context():
            from app.utils.crypto import encrypt_text, decrypt_text
            plain = "kata_sandi_rahasia_©®™"
            cipher = encrypt_text(plain)
            assert decrypt_text(cipher) == plain

    def test_generate_key_returns_valid_fernet_key(self, app):
        with app.app_context():
            from app.utils.crypto import generate_key
            key = generate_key()
            # Fernet key harus valid — ini akan throw jika key invalid
            Fernet(key.encode())
            assert len(key) > 0
