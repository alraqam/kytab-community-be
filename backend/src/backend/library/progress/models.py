from sqlalchemy import Column, BigInteger, ForeignKey, Date, UniqueConstraint, Integer, String, DateTime

from src.backend.core.models import IntIdMixin, TimeActionMixin, Base

class ReadingPeriod  (Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "reading_periods"

    shelf_item_id = Column(BigInteger, ForeignKey("shelf_items.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

class ProgressLog(Base, IntIdMixin, TimeActionMixin):
    __tablename__ = "progress_logs"

    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    period_id = Column(BigInteger, ForeignKey("reading_periods.id", ondelete="CASCADE"), nullable=False)
    pages_read = Column(Integer, nullable=False)
    log_date = Column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "period_id", "log_date", name="uq_user_period_log"),
    )

