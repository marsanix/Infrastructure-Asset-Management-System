"""Model Account — user login aplikasi."""
import bcrypt
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db


class Account(db.Model):
    __tablename__ = "accounts"

    id:                  Mapped[int]            = mapped_column(Integer, primary_key=True)
    username:            Mapped[str]            = mapped_column(String(50), unique=True, nullable=False)
    email:               Mapped[str]            = mapped_column(String(100), unique=True, nullable=False)
    password_hash:       Mapped[str]            = mapped_column(Text, nullable=False)
    role_id:             Mapped[int]            = mapped_column(Integer, db.ForeignKey("roles.id"), nullable=False)
    full_name:           Mapped[str]            = mapped_column(String(150), nullable=False)
    is_active:           Mapped[bool]           = mapped_column(Boolean, default=True)
    is_locked:           Mapped[bool]           = mapped_column(Boolean, default=False)
    failed_login_count:  Mapped[int]            = mapped_column(Integer, default=0)
    last_login_at:       Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_login_ip:       Mapped[str | None]     = mapped_column(String(45))
    password_changed_at: Mapped[datetime]       = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    created_at:          Mapped[datetime]       = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at:          Mapped[datetime]       = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    deleted_at:          Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    role = relationship("Role", back_populates="accounts")

    # ── Password helpers ──────────────────────────────────────
    def set_password(self, plain_password: str) -> None:
        """Hash password dengan bcrypt (cost factor 12)."""
        self.password_hash = bcrypt.hashpw(
            plain_password.encode("utf-8"),
            bcrypt.gensalt(rounds=12),
        ).decode("utf-8")

    def check_password(self, plain_password: str) -> bool:
        """Verifikasi password — timing-safe via bcrypt."""
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            self.password_hash.encode("utf-8"),
        )

    def increment_failed_login(self, max_attempts: int = 5) -> None:
        self.failed_login_count += 1
        if self.failed_login_count >= max_attempts:
            self.is_locked = True

    def reset_failed_login(self) -> None:
        self.failed_login_count = 0
        self.is_locked = False

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def __repr__(self) -> str:
        return f"<Account {self.username}>"


class RefreshToken(db.Model):
    __tablename__ = "refresh_tokens"

    id:         Mapped[int]            = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int]            = mapped_column(Integer, db.ForeignKey("accounts.id", ondelete="CASCADE"))
    token_hash: Mapped[str]            = mapped_column(Text, unique=True, nullable=False)
    expires_at: Mapped[datetime]       = mapped_column(DateTime(timezone=True), nullable=False)
    revoked:    Mapped[bool]           = mapped_column(Boolean, default=False)
    ip_address: Mapped[str | None]     = mapped_column(String(45))
    user_agent: Mapped[str | None]     = mapped_column(Text)
    created_at: Mapped[datetime]       = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
