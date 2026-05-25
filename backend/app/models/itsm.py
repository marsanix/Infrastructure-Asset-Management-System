"""Model ITSM: Change, Incident, Problem, Request."""
import enum
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db


# ── Enums ─────────────────────────────────────────────────────

class ChangeStatus(str, enum.Enum):
    DRAFT       = "Draft"
    SUBMITTED   = "Submitted"
    APPROVED    = "Approved"
    REJECTED    = "Rejected"
    IN_PROGRESS = "In Progress"
    COMPLETED   = "Completed"
    CANCELLED   = "Cancelled"

class ChangePriority(str, enum.Enum):
    LOW      = "Low"
    MEDIUM   = "Medium"
    HIGH     = "High"
    CRITICAL = "Critical"

class ChangeType(str, enum.Enum):
    STANDARD  = "Standard"
    NORMAL    = "Normal"
    EMERGENCY = "Emergency"

class IncidentStatus(str, enum.Enum):
    OPEN        = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED    = "Resolved"
    CLOSED      = "Closed"
    CANCELLED   = "Cancelled"

class IncidentPriority(str, enum.Enum):
    LOW      = "Low"
    MEDIUM   = "Medium"
    HIGH     = "High"
    CRITICAL = "Critical"

class IncidentSeverity(str, enum.Enum):
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"
    S4 = "S4"

class ProblemStatus(str, enum.Enum):
    OPEN              = "Open"
    UNDER_INVESTIGATION = "Under Investigation"
    KNOWN_ERROR       = "Known Error"
    RESOLVED          = "Resolved"
    CLOSED            = "Closed"

class RequestStatus(str, enum.Enum):
    DRAFT       = "Draft"
    SUBMITTED   = "Submitted"
    APPROVED    = "Approved"
    REJECTED    = "Rejected"
    IN_PROGRESS = "In Progress"
    COMPLETED   = "Completed"
    CANCELLED   = "Cancelled"

class RequestPriority(str, enum.Enum):
    LOW    = "Low"
    MEDIUM = "Medium"
    HIGH   = "High"

class RequestType(str, enum.Enum):
    NEW_ASSET   = "New Asset"
    REPAIR      = "Repair"
    REPLACEMENT = "Replacement"
    SOFTWARE    = "Software"
    ACCESS      = "Access"
    OTHER       = "Other"


# ── Change ────────────────────────────────────────────────────

class Change(db.Model):
    __tablename__ = "changes"
    id:             Mapped[int]  = mapped_column(Integer, primary_key=True)
    change_number:  Mapped[str]  = mapped_column(String(20), unique=True, nullable=False)
    title:          Mapped[str]  = mapped_column(String(200), nullable=False)
    description:    Mapped[str | None] = mapped_column(Text)
    change_type:    Mapped[ChangeType]     = mapped_column(Enum(ChangeType,     name="change_type"),     default=ChangeType.NORMAL)
    priority:       Mapped[ChangePriority] = mapped_column(Enum(ChangePriority, name="change_priority"), default=ChangePriority.MEDIUM)
    status:         Mapped[ChangeStatus]   = mapped_column(Enum(ChangeStatus,   name="change_status"),   default=ChangeStatus.DRAFT)
    asset_id:       Mapped[int | None] = mapped_column(Integer, db.ForeignKey("assets.id"))
    requested_by:   Mapped[int | None] = mapped_column(Integer, db.ForeignKey("accounts.id"))
    approved_by:    Mapped[int | None] = mapped_column(Integer, db.ForeignKey("accounts.id"))
    planned_start:  Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    planned_end:    Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    actual_start:   Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    actual_end:     Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rollback_plan:  Mapped[str | None] = mapped_column(Text)
    notes:          Mapped[str | None] = mapped_column(Text)
    created_at:     Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at:     Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted_at:     Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# ── Incident ──────────────────────────────────────────────────

class Incident(db.Model):
    __tablename__ = "incidents"
    id:              Mapped[int]  = mapped_column(Integer, primary_key=True)
    incident_number: Mapped[str]  = mapped_column(String(20), unique=True, nullable=False)
    title:           Mapped[str]  = mapped_column(String(200), nullable=False)
    description:     Mapped[str | None] = mapped_column(Text)
    priority:        Mapped[IncidentPriority] = mapped_column(Enum(IncidentPriority, name="incident_priority"), default=IncidentPriority.MEDIUM)
    severity:        Mapped[IncidentSeverity] = mapped_column(Enum(IncidentSeverity, name="incident_severity"), default=IncidentSeverity.S3)
    status:          Mapped[IncidentStatus]   = mapped_column(Enum(IncidentStatus,   name="incident_status"),   default=IncidentStatus.OPEN)
    asset_id:        Mapped[int | None] = mapped_column(Integer, db.ForeignKey("assets.id"))
    reported_by:     Mapped[int | None] = mapped_column(Integer, db.ForeignKey("accounts.id"))
    assigned_to:     Mapped[int | None] = mapped_column(Integer, db.ForeignKey("accounts.id"))
    resolved_by:     Mapped[int | None] = mapped_column(Integer, db.ForeignKey("accounts.id"))
    reported_at:     Mapped[datetime]   = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at:     Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    closed_at:       Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolution_note: Mapped[str | None] = mapped_column(Text)
    created_at:      Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at:      Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted_at:      Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


# ── Problem ───────────────────────────────────────────────────

class Problem(db.Model):
    __tablename__ = "problems"
    id:             Mapped[int]  = mapped_column(Integer, primary_key=True)
    problem_number: Mapped[str]  = mapped_column(String(20), unique=True, nullable=False)
    title:          Mapped[str]  = mapped_column(String(200), nullable=False)
    description:    Mapped[str | None] = mapped_column(Text)
    root_cause:     Mapped[str | None] = mapped_column(Text)
    workaround:     Mapped[str | None] = mapped_column(Text)
    status:         Mapped[ProblemStatus] = mapped_column(Enum(ProblemStatus, name="problem_status"), default=ProblemStatus.OPEN)
    asset_id:       Mapped[int | None] = mapped_column(Integer, db.ForeignKey("assets.id"))
    reported_by:    Mapped[int | None] = mapped_column(Integer, db.ForeignKey("accounts.id"))
    assigned_to:    Mapped[int | None] = mapped_column(Integer, db.ForeignKey("accounts.id"))
    resolved_by:    Mapped[int | None] = mapped_column(Integer, db.ForeignKey("accounts.id"))
    resolved_at:    Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at:     Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at:     Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted_at:     Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class IncidentProblem(db.Model):
    __tablename__ = "incident_problems"
    incident_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("incidents.id", ondelete="CASCADE"), primary_key=True)
    problem_id:  Mapped[int] = mapped_column(Integer, db.ForeignKey("problems.id",  ondelete="CASCADE"), primary_key=True)


# ── Request ───────────────────────────────────────────────────

class Request(db.Model):
    __tablename__ = "requests"
    id:             Mapped[int]  = mapped_column(Integer, primary_key=True)
    request_number: Mapped[str]  = mapped_column(String(20), unique=True, nullable=False)
    title:          Mapped[str]  = mapped_column(String(200), nullable=False)
    description:    Mapped[str | None] = mapped_column(Text)
    request_type:   Mapped[RequestType]     = mapped_column(Enum(RequestType,     name="request_type"),     default=RequestType.OTHER)
    priority:       Mapped[RequestPriority] = mapped_column(Enum(RequestPriority, name="request_priority"), default=RequestPriority.MEDIUM)
    status:         Mapped[RequestStatus]   = mapped_column(Enum(RequestStatus,   name="request_status"),   default=RequestStatus.DRAFT)
    asset_id:       Mapped[int | None] = mapped_column(Integer, db.ForeignKey("assets.id"))
    requested_by:   Mapped[int | None] = mapped_column(Integer, db.ForeignKey("accounts.id"))
    approved_by:    Mapped[int | None] = mapped_column(Integer, db.ForeignKey("accounts.id"))
    fulfilled_by:   Mapped[int | None] = mapped_column(Integer, db.ForeignKey("accounts.id"))
    approved_at:    Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fulfilled_at:   Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes:          Mapped[str | None] = mapped_column(Text)
    created_at:     Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at:     Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    deleted_at:     Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
