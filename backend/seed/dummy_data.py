"""Seed realistic DUMMY data so the dashboard / profile / admin views show content.

Creates a few demo students and gives them (and the admin) enrollments, submissions,
and lesson progress. Idempotent: re-running wipes only these users' progress rows and
recreates them.

Run from backend/:  python seed/dummy_data.py
"""

from __future__ import annotations

import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete, func, select  # noqa: E402

from app.core.database import SessionLocal, engine  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models import (  # noqa: E402
    Base,
    Course,
    Enrollment,
    Exercise,
    Lesson,
    LessonProgress,
    Module,
    ProgressStatus,
    Submission,
    SubmissionStatus,
    User,
    UserRole,
)

random.seed(42)
NOW = datetime.now(timezone.utc)

DEMO_STUDENTS = [
    ("student@codewithtlp.com", "demostudent", "Demo Student", "student123"),
    ("maya@codewithtlp.com", "maya", "Maya Rahman", "student123"),
    ("daniel@codewithtlp.com", "daniel", "Daniel Kim", "student123"),
    ("aisha@codewithtlp.com", "aisha", "Aisha Malik", "student123"),
]

# A spread of outcomes for variety in the tables/charts.
STATUS_POOL = (
    [SubmissionStatus.accepted] * 6
    + [SubmissionStatus.wrong_answer] * 2
    + [SubmissionStatus.time_limit_exceeded, SubmissionStatus.runtime_error]
)


def ensure_student(db, email, username, full_name, password) -> User:
    user = db.scalar(select(User).where(User.email == email))
    if user:
        return user
    user = User(
        email=email,
        username=username,
        full_name=full_name,
        hashed_password=hash_password(password),
        role=UserRole.student,
        is_active=True,
        bio=f"{full_name} — learning CS on Code with TLP.",
    )
    db.add(user)
    db.flush()
    return user


def seed_for_user(db, user: User, courses, exercises) -> dict:
    stats = {"enrollments": 0, "submissions": 0, "progress": 0}

    # ── Enrollments ──────────────────────────────────────────
    chosen_courses = random.sample(courses, k=min(6, len(courses)))
    percents = [100.0, 100.0, 78.0, 55.0, 33.0, 12.0]
    for course, pct in zip(chosen_courses, percents):
        enr = Enrollment(
            user_id=user.id,
            course_id=course.id,
            progress_percent=pct,
            completed_at=NOW - timedelta(days=random.randint(1, 10)) if pct >= 100 else None,
            created_at=NOW - timedelta(days=random.randint(12, 40)),
        )
        db.add(enr)
        stats["enrollments"] += 1

        # Lesson progress consistent with the course %.
        lessons = [l for m in course.modules for l in m.lessons]
        n_done = int(len(lessons) * pct / 100)
        for i, lesson in enumerate(lessons):
            status = ProgressStatus.completed if i < n_done else (
                ProgressStatus.in_progress if i == n_done else ProgressStatus.not_started
            )
            if status == ProgressStatus.not_started:
                continue
            db.add(LessonProgress(
                user_id=user.id,
                lesson_id=lesson.id,
                status=status,
                completed_at=NOW - timedelta(days=random.randint(1, 20)) if status == ProgressStatus.completed else None,
                created_at=NOW - timedelta(days=random.randint(2, 30)),
            ))
            stats["progress"] += 1

    # ── Submissions ──────────────────────────────────────────
    chosen_ex = random.sample(exercises, k=min(18, len(exercises)))
    for idx, ex in enumerate(chosen_ex):
        status = random.choice(STATUS_POOL)
        langs = ex.supported_languages or ["python"]
        language = random.choice(langs)
        total = max(3, len(ex.test_cases) or random.randint(3, 6))
        if status == SubmissionStatus.accepted:
            passed, score = total, float(ex.points)
        elif status == SubmissionStatus.wrong_answer:
            passed = random.randint(0, total - 1)
            score = round(ex.points * passed / total, 1)
        else:
            passed, score = 0, 0.0
        db.add(Submission(
            user_id=user.id,
            exercise_id=ex.id,
            language=language,
            code=f"# {language} solution attempt for exercise #{ex.id}\n",
            status=status,
            score=score,
            passed_tests=passed,
            total_tests=total,
            runtime_ms=random.randint(8, 1800),
            memory_kb=random.randint(2048, 65536),
            created_at=NOW - timedelta(days=random.randint(0, 21), hours=random.randint(0, 23)),
        ))
        stats["submissions"] += 1

    return stats


def seed_dummy() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        courses = db.scalars(
            select(Course).where(Course.is_published.is_(True))
        ).all()
        # eager-load modules/lessons
        courses = [db.get(Course, c.id) for c in courses]
        exercises = db.scalars(select(Exercise).where(Exercise.is_published.is_(True))).all()
        if not courses or not exercises:
            print("No published courses/exercises found — run the course import first.")
            return

        # Target users: the admin + demo students.
        admin = db.scalar(select(User).where(User.role == UserRole.admin))
        targets = [admin] if admin else []
        for email, username, name, pw in DEMO_STUDENTS:
            targets.append(ensure_student(db, email, username, name, pw))
        targets = [u for u in targets if u]
        db.flush()

        user_ids = [u.id for u in targets]
        # Idempotent reset of just these users' progress rows.
        db.execute(delete(Submission).where(Submission.user_id.in_(user_ids)))
        db.execute(delete(Enrollment).where(Enrollment.user_id.in_(user_ids)))
        db.execute(delete(LessonProgress).where(LessonProgress.user_id.in_(user_ids)))
        db.flush()

        print("=" * 60)
        for u in targets:
            s = seed_for_user(db, u, courses, exercises)
            print(f"  {u.email:<30} {s['enrollments']} enr · {s['submissions']} subs · {s['progress']} progress")
        db.commit()

        print("-" * 60)
        print(f"  Users seeded: {len(targets)}")
        print(f"  Total submissions: {db.scalar(select(func.count(Submission.id)))}")
        print(f"  Total enrollments: {db.scalar(select(func.count(Enrollment.id)))}")
        print("  Demo student login:  student@codewithtlp.com / student123")
        print("=" * 60)


if __name__ == "__main__":
    seed_dummy()
