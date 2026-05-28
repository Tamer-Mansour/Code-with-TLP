from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    pass


class InterviewCategory(Base, TimestampMixin):
    """A topic area for interview prep, e.g. 'System Design', 'Algorithms'."""

    __tablename__ = "interview_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str | None] = mapped_column(String(64))
    color: Mapped[str | None] = mapped_column(String(16))
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    questions: Mapped[list["InterviewQuestion"]] = relationship(
        back_populates="category",
        cascade="all, delete-orphan",
        order_by="InterviewQuestion.order_index",
    )


class InterviewQuestion(Base, TimestampMixin):
    """One interview question with its (markdown) answer."""

    __tablename__ = "interview_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("interview_categories.id", ondelete="CASCADE"), index=True, nullable=False
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)  # markdown
    difficulty: Mapped[str] = mapped_column(String(16), default="medium", nullable=False)
    tags: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    category: Mapped["InterviewCategory"] = relationship(back_populates="questions")
