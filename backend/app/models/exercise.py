import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin
from app.models.catalog import exercise_tags

if TYPE_CHECKING:
    from app.models.catalog import Lesson, Tag
    from app.models.submission import Submission


class Difficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class Exercise(Base, TimestampMixin):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    lesson_id: Mapped[int | None] = mapped_column(ForeignKey("lessons.id", ondelete="SET NULL"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    prompt_md: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(Enum(Difficulty), default=Difficulty.easy, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # JSON maps {"python": "def solve(...): ...", "javascript": "function solve(...){}", ...}
    starter_code: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    solution_code: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    # Subset of supported languages, e.g. ["python", "javascript"]
    supported_languages: Mapped[list] = mapped_column(JSON, default=list, nullable=False)

    time_limit_ms: Mapped[int] = mapped_column(Integer, default=2000, nullable=False)
    memory_limit_mb: Mapped[int] = mapped_column(Integer, default=256, nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=10, nullable=False)

    lesson: Mapped["Lesson | None"] = relationship(back_populates="exercises")
    tags: Mapped[list["Tag"]] = relationship(secondary=exercise_tags, back_populates="exercises")
    test_cases: Mapped[list["TestCase"]] = relationship(
        back_populates="exercise",
        cascade="all, delete-orphan",
        order_by="TestCase.order_index",
    )
    submissions: Mapped[list["Submission"]] = relationship(back_populates="exercise", cascade="all, delete-orphan")


class TestCase(Base, TimestampMixin):
    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(128))
    stdin: Mapped[str] = mapped_column(Text, default="", nullable=False)
    expected_stdout: Mapped[str] = mapped_column(Text, default="", nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    weight: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    exercise: Mapped["Exercise"] = relationship(back_populates="test_cases")
