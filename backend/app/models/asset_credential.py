"""Model AssetCredential — password perangkat (AES-256 encrypted)."""
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db
from ..utils.crypto import encrypt_text, decrypt_text


class AssetCredential(db.Model):
    __tablename__ = "asset_credentials"

    id:                  Mapped[int]        = mapped_column(Integer, primary_key=True)
    asset_id:            Mapped[int]        = mapped_column(Integer, db.ForeignKey("assets.id", ondelete="CASCADE"), nullable=False)
    credential_type:     Mapped[str]        = mapped_column(String(50), nullable=False)  # SSH, Web Console, SNMP, Telnet
    username:            Mapped[str | None] = mapped_column(Text)
    # Kolom ini menyimpan ciphertext — JANGAN pernah simpan plaintext
    password_encrypted:  Mapped[str]        = mapped_column(Text, nullable=False)
    notes:               Mapped[str | None] = mapped_column(Text)
    created_by:          Mapped[int | None] = mapped_column(Integer, db.ForeignKey("accounts.id"))
    created_at:          Mapped[datetime]   = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at:          Mapped[datetime]   = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    asset = relationship("Asset", back_populates="credentials")

    def set_password(self, plain_password: str) -> None:
        """Enkripsi password sebelum disimpan ke DB."""
        self.password_encrypted = encrypt_text(plain_password)

    def get_password(self) -> str:
        """Dekripsi password dari DB."""
        return decrypt_text(self.password_encrypted)
