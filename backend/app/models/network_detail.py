from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db

class NetworkDetail(db.Model):
    __tablename__ = "network_details"
    asset_id:      Mapped[int]        = mapped_column(Integer, db.ForeignKey("assets.id", ondelete="CASCADE"), primary_key=True)
    ip_address:    Mapped[str | None] = mapped_column(String(45))
    mac_address:   Mapped[str | None] = mapped_column(String(17))
    subnet_mask:   Mapped[str | None] = mapped_column(String(45))
    gateway:       Mapped[str | None] = mapped_column(String(45))
    dns_primary:   Mapped[str | None] = mapped_column(String(45))
    dns_secondary: Mapped[str | None] = mapped_column(String(45))
    vlan:          Mapped[str | None] = mapped_column(String(20))
    hostname:      Mapped[str | None] = mapped_column(String(100))
    updated_at:    Mapped[datetime]   = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    asset = relationship("Asset", back_populates="network_detail")
