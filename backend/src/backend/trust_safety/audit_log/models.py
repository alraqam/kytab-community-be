from datetime import datetime

from sqlalchemy import Column, BigInteger, ForeignKey, String, Text, DateTime, event, select
from sqlalchemy.orm import column_property

from src.backend.core.models import Base, IntIdMixin
from src.backend.identity.auth.models import User
from src.backend.trust_safety.audit_log.exceptions import AuditLogImmutableError


class AuditLog(Base, IntIdMixin):
    """ORM model representing an immutable record of a moderation or administrative action. Entries have no updated_at: they are append-only."""

    __tablename__ = "audit_log"

    actor_id = Column(BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False)
    object_type = Column(String(100), nullable=False)
    object_id = Column(BigInteger, nullable=False)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

AuditLog.actor_username = column_property(
    select(User.username).where(User.id == AuditLog.actor_id).correlate_except(User).scalar_subquery()
)

@event.listens_for(AuditLog, "before_update")
def _forbid_update(mapper, connection, target):
    """Blocks any UPDATE against an audit log row, enforcing immutability at the ORM level."""
    raise AuditLogImmutableError("Audit log entries cannot be modified")

@event.listens_for(AuditLog, "before_delete")
def _forbid_delete(mapper, connection, target):
    """Blocks any DELETE against an audit log row, enforcing immutability at the ORM level."""
    raise AuditLogImmutableError("Audit log entries cannot be deleted")
