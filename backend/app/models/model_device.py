from datetime import datetime, timezone
from sqlalchemy import String, Boolean, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db

class DeviceModel(db.Model):
    __tablename__ = "models"
    id:             Mapped[int]  = mapped_column(Integer, primary_key=True)
    name:           Mapped[str]  = mapped_column(String(100), nullable=False)
    specifications: Mapped[str | None] = mapped_column(Text)
    brand_id:       Mapped[int | None] = mapped_column(Integer, db.ForeignKey("brands.id"))
    category_id:    Mapped[int | None] = mapped_column(Integer, db.ForeignKey("categories.id"))
    is_active:      Mapped[bool] = mapped_column(Boolean, default=True)
    created_at:     Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at:     Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted_at:     Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
