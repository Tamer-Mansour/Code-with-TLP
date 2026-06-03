from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class LearningProfile(Base, TimestampMixin):
    """A learner's stated goals & interests, captured by the onboarding wizard.

    Drives the personalized learning curve and the "interested-first" ordering
    of the catalog. One row per user (1:1), created lazily on first save.
    """

    __tablename__ = "learning_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Primary motivation: career | school | interview | hobby | upskill
    goal: Mapped[str | None] = mapped_column(String(32))
    # Self-rated experience: new | beginner | intermediate | advanced
    experience_level: Mapped[str | None] = mapped_column(String(32))
    # Weekly time commitment in hours (used to project completion pace).
    weekly_hours: Mapped[int | None] = mapped_column(Integer)

    # Interest tags chosen in the wizard, e.g. ["web", "algorithms", "data"].
    interests: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    # Preferred languages, e.g. ["python", "javascript"].
    languages: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    # True once the wizard has been completed at least once.
    onboarded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship(back_populates="learning_profile")
