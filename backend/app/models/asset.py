"""Model Asset."""
import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Date, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db


class AssetStatus(str, enum.Enum):
    ACTIVE    = "Active"
    AVAILABLE = "Available"
    REPAIR    = "Repair"
    DISPOSED  = "Disposed"


class Asset(db.Model):
    __tablename__ = "assets"

    id:              Mapped[int]            = mapped_column(Integer, primary_key=True)
    asset_tag:       Mapped[str]            = mapped_column(String(50), unique=True, nullable=False)
    serial_number:   Mapped[str]            = mapped_column(String(100), unique=True, nullable=False)
    po_number:       Mapped[str | None]     = mapped_column(String(100))
    model_id:        Mapped[int]            = mapped_column(Integer, db.ForeignKey("models.id"), nullable=False)
    location_id:     Mapped[int]            = mapped_column(Integer, db.ForeignKey("locations.id"), nullable=False)
    employee_id:     Mapped[int | None]     = mapped_column(Integer, db.ForeignKey("employees.id"))
    status:          Mapped[AssetStatus]    = mapped_column(
        Enum(AssetStatus, name="asset_status"), default=AssetStatus.AVAILABLE, nullable=False
    )
    purchase_date:   Mapped[datetime | None] = mapped_column(Date)
    warranty_months: Mapped[int | None]     = mapped_column(Integer)
    os_license:      Mapped[str | None]     = mapped_column(String(100))
    notes:           Mapped[str | None]     = mapped_column(Text)
    created_by:      Mapped[int | None]     = mapped_column(Integer, db.ForeignKey("accounts.id"))
    created_at:      Mapped[datetime]       = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at:      Mapped[datetime]       = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
    deleted_at:      Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    model           = relationship("DeviceModel", backref="assets")
    location        = relationship("Location", backref="assets")
    employee        = relationship("Employee", backref="assets")
    network_detail  = relationship("NetworkDetail", back_populates="asset", uselist=False, cascade="all, delete-orphan")
    credentials     = relationship("AssetCredential", back_populates="asset", cascade="all, delete-orphan")

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
