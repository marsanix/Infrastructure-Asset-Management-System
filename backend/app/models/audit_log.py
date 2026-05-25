"""Model AuditLog."""
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id:         Mapped[int]            = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int | None]     = mapped_column(Integer, db.ForeignKey("accounts.id"))
    action:     Mapped[str]            = mapped_column(String(50), nullable=False)   # CREATE, UPDATE, DELETE, LOGIN, LOGOUT
    module:     Mapped[str]            = mapped_column(String(50), nullable=False)   # asset, account, incident, ...
    record_id:  Mapped[int | None]     = mapped_column(Integer)
    old_data:   Mapped[dict | None]    = mapped_column(JSON)
    new_data:   Mapped[dict | None]    = mapped_column(JSON)
    ip_address: Mapped[str | None]     = mapped_column(String(45))
    user_agent: Mapped[str | None]     = mapped_column(Text)
    created_at: Mapped[datetime]       = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
