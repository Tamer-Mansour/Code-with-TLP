import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.exercise import Exercise, TestCase
    from app.models.user import User


class SubmissionStatus(str, enum.Enum):
    pending = "pending"
    running = "running"
    accepted = "accepted"
    wrong_answer = "wrong_answer"
    time_limit_exceeded = "time_limit_exceeded"
    memory_limit_exceeded = "memory_limit_exceeded"
    runtime_error = "runtime_error"
    compile_error = "compile_error"
    internal_error = "internal_error"


class Submission(Base, TimestampMixin):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"), index=True, nullable=False)
    language: Mapped[str] = mapped_column(String(32), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[SubmissionStatus] = mapped_column(Enum(SubmissionStatus), default=SubmissionStatus.pending, nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    passed_tests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_tests: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    runtime_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    memory_kb: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stdout: Mapped[str | None] = mapped_column(Text)
    stderr: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="submissions")
    exercise: Mapped["Exercise"] = relationship(back_populates="submissions")
    results: Mapped[list["TestCaseResult"]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
        order_by="TestCaseResult.id",
    )


class TestCaseResult(Base, TimestampMixin):
    __tablename__ = "test_case_results"

    id: Mapped[int] = mapped_column(primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id", ondelete="CASCADE"), index=True, nullable=False)
    test_case_id: Mapped[int] = mapped_column(ForeignKey("test_cases.id", ondelete="CASCADE"), index=True, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    actual_stdout: Mapped[str | None] = mapped_column(Text)
    stderr: Mapped[str | None] = mapped_column(Text)
    runtime_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error: Mapped[str | None] = mapped_column(Text)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    submission: Mapped["Submission"] = relationship(back_populates="results")
    test_case: Mapped["TestCase"] = relationship()
