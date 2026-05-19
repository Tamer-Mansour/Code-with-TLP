"""Seed sample data: admin user, a couple of subjects, one course with a module + lessons,
and a 'sum two numbers' exercise with test cases.

Run with: python -m app.seed
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.core.security import hash_password
from app.models import (
    Base,
    Course,
    Difficulty,
    Exercise,
    Lesson,
    LessonType,
    Module,
    Subject,
    TestCase,
    User,
    UserRole,
)

PYTHON_STARTER = """\
# Read two integers from stdin and print their sum.
import sys

def solve():
    a, b = map(int, sys.stdin.read().split())
    print(a + b)

solve()
"""

PYTHON_SOLUTION = PYTHON_STARTER

JS_STARTER = """\
// Read two integers from stdin and print their sum.
const data = require('fs').readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);
console.log(data[0] + data[1]);
"""

TS_STARTER = """\
// Read two integers from stdin and print their sum.
import * as fs from 'fs';
const [a, b] = fs.readFileSync(0, 'utf8').trim().split(/\\s+/).map(Number);
console.log(a + b);
"""

JAVA_STARTER = """\
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        long a = sc.nextLong();
        long b = sc.nextLong();
        System.out.println(a + b);
    }
}
"""

CSHARP_STARTER = """\
// dotnet script — read two integers and print their sum.
var input = Console.In.ReadToEnd().Split(new[] {' ', '\\n', '\\r', '\\t'}, StringSplitOptions.RemoveEmptyEntries);
Console.WriteLine(long.Parse(input[0]) + long.Parse(input[1]));
"""


def ensure_admin(db: Session) -> User:
    user = db.scalar(select(User).where(User.email == settings.first_admin_email))
    if user:
        return user
    user = User(
        email=settings.first_admin_email,
        username=settings.first_admin_username,
        full_name="Site Administrator",
        hashed_password=hash_password(settings.first_admin_password),
        role=UserRole.admin,
        is_active=True,
    )
    db.add(user)
    db.flush()
    return user


def ensure_subject(db: Session, slug: str, **kwargs) -> Subject:
    subj = db.scalar(select(Subject).where(Subject.slug == slug))
    if subj:
        return subj
    subj = Subject(slug=slug, **kwargs)
    db.add(subj)
    db.flush()
    return subj


def ensure_course(db: Session, subject: Subject, slug: str, **kwargs) -> Course:
    course = db.scalar(select(Course).where(Course.slug == slug))
    if course:
        return course
    course = Course(subject_id=subject.id, slug=slug, **kwargs)
    db.add(course)
    db.flush()
    return course


def ensure_module(db: Session, course: Course, title: str, order_index: int) -> Module:
    module = db.scalar(
        select(Module).where(Module.course_id == course.id, Module.title == title)
    )
    if module:
        return module
    module = Module(course_id=course.id, title=title, order_index=order_index)
    db.add(module)
    db.flush()
    return module


def ensure_lesson(db: Session, module: Module, slug: str, **kwargs) -> Lesson:
    lesson = db.scalar(
        select(Lesson).where(Lesson.module_id == module.id, Lesson.slug == slug)
    )
    if lesson:
        return lesson
    lesson = Lesson(module_id=module.id, slug=slug, **kwargs)
    db.add(lesson)
    db.flush()
    return lesson


def ensure_exercise(db: Session, lesson: Lesson, slug: str, **kwargs) -> Exercise:
    exercise = db.scalar(select(Exercise).where(Exercise.slug == slug))
    if exercise:
        return exercise
    exercise = Exercise(lesson_id=lesson.id, slug=slug, **kwargs)
    db.add(exercise)
    db.flush()
    return exercise


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ensure_admin(db)

        algos = ensure_subject(
            db,
            slug="algorithms",
            name="Algorithms",
            description="Core algorithms and data structures.",
            icon="cpu",
            color="#3b82f6",
            order_index=1,
        )
        web = ensure_subject(
            db,
            slug="web-development",
            name="Web Development",
            description="Build modern web applications.",
            icon="globe",
            color="#10b981",
            order_index=2,
        )
        ensure_subject(
            db,
            slug="databases",
            name="Databases",
            description="Relational and non-relational data systems.",
            icon="database",
            color="#f59e0b",
            order_index=3,
        )

        course = ensure_course(
            db,
            algos,
            slug="intro-to-algorithms",
            title="Introduction to Algorithms",
            summary="Master the foundations every CS student needs.",
            description="A hands-on tour of complexity, recursion, sorting, searching, and basic data structures.",
            difficulty="beginner",
            estimated_hours=12,
            is_published=True,
            order_index=1,
        )

        ensure_course(
            db,
            web,
            slug="modern-frontend-angular",
            title="Modern Frontend with Angular",
            summary="From components to signals and standalone APIs.",
            description="Learn Angular by building real features step by step.",
            difficulty="intermediate",
            estimated_hours=20,
            is_published=True,
            order_index=1,
        )

        module1 = ensure_module(db, course, "Getting Started", order_index=1)
        ensure_module(db, course, "Big-O Notation", order_index=2)

        intro_lesson = ensure_lesson(
            db,
            module1,
            slug="what-is-an-algorithm",
            title="What is an algorithm?",
            lesson_type=LessonType.reading,
            content_md=(
                "# What is an algorithm?\n\n"
                "An algorithm is a well-defined sequence of steps that solves a problem.\n\n"
                "## Why study them?\n\n"
                "Good algorithms power fast software — even small inputs become slow under bad ones."
            ),
            duration_minutes=5,
            order_index=1,
        )

        practice_lesson = ensure_lesson(
            db,
            module1,
            slug="first-practice",
            title="First practice",
            lesson_type=LessonType.exercise,
            content_md="Solve the warm-up exercise below.",
            duration_minutes=10,
            order_index=2,
        )

        exercise = ensure_exercise(
            db,
            practice_lesson,
            slug="sum-two-numbers",
            title="Sum two numbers",
            prompt_md=(
                "# Sum two numbers\n\n"
                "Read two integers `a` and `b` from standard input, separated by whitespace, "
                "and print their sum on a single line.\n\n"
                "**Example**\n\n"
                "Input:\n```\n3 5\n```\n\n"
                "Output:\n```\n8\n```"
            ),
            difficulty=Difficulty.easy,
            is_published=True,
            starter_code={
                "python": PYTHON_STARTER,
                "javascript": JS_STARTER,
                "typescript": TS_STARTER,
                "java": JAVA_STARTER,
                "csharp": CSHARP_STARTER,
            },
            solution_code={
                "python": PYTHON_SOLUTION,
            },
            supported_languages=["python", "javascript", "typescript", "java", "csharp"],
            time_limit_ms=3000,
            memory_limit_mb=256,
            points=10,
        )

        # Test cases (only seed if the exercise has none).
        if not exercise.test_cases:
            for idx, (stdin, expected, hidden) in enumerate(
                [
                    ("3 5\n", "8", False),
                    ("0 0\n", "0", False),
                    ("-7 10\n", "3", True),
                    ("100000 200000\n", "300000", True),
                ]
            ):
                db.add(
                    TestCase(
                        exercise_id=exercise.id,
                        name=f"case-{idx + 1}",
                        stdin=stdin,
                        expected_stdout=expected,
                        is_hidden=hidden,
                        weight=1,
                        order_index=idx,
                    )
                )

        db.commit()
        print("Seed completed.")
        print(f"  Admin email:    {settings.first_admin_email}")
        print(f"  Admin password: {settings.first_admin_password}")


if __name__ == "__main__":
    seed()
