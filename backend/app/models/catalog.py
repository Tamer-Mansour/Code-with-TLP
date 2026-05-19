import enum
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text, UniqueConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.exercise import Exercise
    from app.models.progress import Enrollment, LessonProgress


class LessonType(str, enum.Enum):
    reading = "reading"
    video = "video"
    quiz = "quiz"
    exercise = "exercise"


exercise_tags = Table(
    "exercise_tags",
    Base.metadata,
    Column("exercise_id", ForeignKey("exercises.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


learning_path_courses = Table(
    "learning_path_courses",
    Base.metadata,
    Column("path_id", ForeignKey("learning_paths.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
    Column("order_index", Integer, default=0, nullable=False),
)


class Subject(Base, TimestampMixin):
    """A top-level area of study, e.g. 'Algorithms', 'Web Development', 'Databases'."""

    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    icon: Mapped[str | None] = mapped_column(String(64))
    color: Mapped[str | None] = mapped_column(String(16))
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    courses: Mapped[list["Course"]] = relationship(back_populates="subject", cascade="all, delete-orphan")


class Course(Base, TimestampMixin):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    summary: Mapped[str | None] = mapped_column(String(512))
    description: Mapped[str | None] = mapped_column(Text)
    cover_image: Mapped[str | None] = mapped_column(String(512))
    difficulty: Mapped[str] = mapped_column(String(32), default="beginner", nullable=False)
    estimated_hours: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_published: Mapped[bool] = mapped_column(default=False, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    subject: Mapped["Subject"] = relationship(back_populates="courses")
    modules: Mapped[list["Module"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="Module.order_index",
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="course", cascade="all, delete-orphan")
    paths: Mapped[list["LearningPath"]] = relationship(secondary=learning_path_courses, back_populates="courses")


class Module(Base, TimestampMixin):
    """A section of a course that groups related lessons."""

    __tablename__ = "modules"

    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str | None] = mapped_column(String(512))
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    course: Mapped["Course"] = relationship(back_populates="modules")
    lessons: Mapped[list["Lesson"]] = relationship(
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="Lesson.order_index",
    )


class Lesson(Base, TimestampMixin):
    __tablename__ = "lessons"

    id: Mapped[int] = mapped_column(primary_key=True)
    module_id: Mapped[int] = mapped_column(ForeignKey("modules.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    lesson_type: Mapped[LessonType] = mapped_column(Enum(LessonType), default=LessonType.reading, nullable=False)
    content_md: Mapped[str | None] = mapped_column(Text)
    video_url: Mapped[str | None] = mapped_column(String(512))
    duration_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    __table_args__ = (UniqueConstraint("module_id", "slug", name="uq_lesson_module_slug"),)

    module: Mapped["Module"] = relationship(back_populates="lessons")
    exercises: Mapped[list["Exercise"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")
    progress: Mapped[list["LessonProgress"]] = relationship(back_populates="lesson", cascade="all, delete-orphan")


class Tag(Base, TimestampMixin):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    exercises: Mapped[list["Exercise"]] = relationship(secondary=exercise_tags, back_populates="tags")


class LearningPath(Base, TimestampMixin):
    """A curated sequence of courses (e.g. 'Become a Backend Engineer')."""

    __tablename__ = "learning_paths"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    cover_image: Mapped[str | None] = mapped_column(String(512))
    is_published: Mapped[bool] = mapped_column(default=False, nullable=False)

    courses: Mapped[list["Course"]] = relationship(secondary=learning_path_courses, back_populates="paths")
