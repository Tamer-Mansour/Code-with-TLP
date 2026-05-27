from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class QuizQuestion(Base, TimestampMixin):
    """A single multiple-choice question belonging to a (quiz-type) lesson."""

    __tablename__ = "quiz_questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), index=True, nullable=False
    )
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    # Ordered list of answer option strings.
    options: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    correct_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    answers: Mapped[list["QuizAnswer"]] = relationship(
        back_populates="question", cascade="all, delete-orphan"
    )


class QuizAnswer(Base, TimestampMixin):
    """A user's stored answer to one quiz question (latest answer kept)."""

    __tablename__ = "quiz_answers"
    __table_args__ = (UniqueConstraint("user_id", "question_id", name="uq_quiz_answer_user_question"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    question_id: Mapped[int] = mapped_column(
        ForeignKey("quiz_questions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    selected_index: Mapped[int] = mapped_column(Integer, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    question: Mapped["QuizQuestion"] = relationship(back_populates="answers")
    user: Mapped["User"] = relationship()
