"""Model Role, Permission, RolePermission — RBAC."""
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db


class Permission(db.Model):
    __tablename__ = "permissions"

    id:          Mapped[int] = mapped_column(Integer, primary_key=True)
    name:        Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    module:      Mapped[str] = mapped_column(String(50), nullable=False)
    action:      Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    created_at:  Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class RolePermission(db.Model):
    __tablename__ = "role_permissions"

    role_id:       Mapped[int] = mapped_column(Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)


class Role(db.Model):
    __tablename__ = "roles"

    id:          Mapped[int]  = mapped_column(Integer, primary_key=True)
    name:        Mapped[str]  = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active:   Mapped[bool] = mapped_column(Boolean, default=True)
    created_at:  Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at:  Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    accounts    = relationship("Account", back_populates="role")
    permissions = relationship("Permission", secondary="role_permissions")

    def has_permission(self, permission_name: str) -> bool:
        return any(p.name == permission_name for p in self.permissions)
