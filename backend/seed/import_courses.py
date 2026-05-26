"""Generic course importer.

Reads every `backend/seed/courses/<dir>/course.yaml` (plus the markdown files it
references) and loads it into the database. Reuses the idempotent `ensure_*`
helpers from `app.seed`, so it is safe to re-run.

Run from the backend/ directory:

    python seed/import_courses.py            # create tables (if needed) + import
    python seed/import_courses.py --reset    # DROP all tables, recreate, then import

`--reset` wipes EVERYTHING (users, submissions, progress). Use it for a clean
rebuild of the catalog. The admin user is always re-created from settings.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select  # noqa: E402

from app.core.database import SessionLocal, engine  # noqa: E402
from app.models import (  # noqa: E402
    Base,
    Difficulty,
    LessonType,
    Tag,
    TestCase,
)
from app.seed import (  # noqa: E402
    ensure_admin,
    ensure_course,
    ensure_exercise,
    ensure_lesson,
    ensure_module,
    ensure_subject,
)

COURSES_DIR = Path(__file__).resolve().parent / "courses"


def _slugify(value: str) -> str:
    out = "".join(c if c.isalnum() else "-" for c in value.lower())
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


def _read_md(course_dir: Path, rel: str | None) -> str | None:
    if not rel:
        return None
    path = course_dir / rel
    if not path.exists():
        raise FileNotFoundError(f"  referenced markdown not found: {path}")
    return path.read_text(encoding="utf-8")


def ensure_tag(db, name: str) -> Tag:
    slug = _slugify(name)
    tag = db.scalar(select(Tag).where(Tag.slug == slug))
    if tag:
        return tag
    tag = Tag(name=name, slug=slug)
    db.add(tag)
    db.flush()
    return tag


def import_course(db, course_dir: Path) -> dict:
    data = yaml.safe_load((course_dir / "course.yaml").read_text(encoding="utf-8"))
    stats = {"modules": 0, "lessons": 0, "exercises": 0, "test_cases": 0}

    s = data["subject"]
    subject = ensure_subject(
        db,
        slug=s["slug"],
        name=s["name"],
        description=s.get("description"),
        icon=s.get("icon"),
        color=s.get("color"),
        order_index=s.get("order_index", 0),
    )

    c = data["course"]
    course = ensure_course(
        db,
        subject,
        slug=c["slug"],
        title=c["title"],
        summary=c.get("summary"),
        description=c.get("description"),
        difficulty=c.get("difficulty", "beginner"),
        estimated_hours=c.get("estimated_hours", 0),
        is_published=c.get("is_published", True),
        order_index=c.get("order_index", 0),
    )

    for m in data.get("modules", []):
        module = ensure_module(db, course, title=m["title"], order_index=m.get("order_index", 0))
        if m.get("summary") and not module.summary:
            module.summary = m["summary"]
        stats["modules"] += 1

        for li, lesson_def in enumerate(m.get("lessons", []), start=1):
            lesson = ensure_lesson(
                db,
                module,
                slug=lesson_def["slug"],
                title=lesson_def["title"],
                lesson_type=LessonType(lesson_def.get("type", "reading")),
                content_md=_read_md(course_dir, lesson_def.get("content_file"))
                or lesson_def.get("content_md"),
                video_url=lesson_def.get("video_url"),
                duration_minutes=lesson_def.get("duration_minutes", 0),
                order_index=lesson_def.get("order_index", li),
            )
            stats["lessons"] += 1

            for ex_def in lesson_def.get("exercises", []) or []:
                exercise = ensure_exercise(
                    db,
                    lesson,
                    slug=ex_def["slug"],
                    title=ex_def["title"],
                    prompt_md=_read_md(course_dir, ex_def.get("prompt_file"))
                    or ex_def.get("prompt", ""),
                    difficulty=Difficulty(ex_def.get("difficulty", "easy")),
                    is_published=ex_def.get("is_published", True),
                    starter_code=ex_def.get("starter_code", {}) or {},
                    solution_code=ex_def.get("solution_code", {}) or {},
                    supported_languages=ex_def.get("supported_languages", ["python"]),
                    time_limit_ms=ex_def.get("time_limit_ms", 3000),
                    memory_limit_mb=ex_def.get("memory_limit_mb", 256),
                    points=ex_def.get("points", 10),
                )
                stats["exercises"] += 1

                for tag_name in ex_def.get("tags", []) or []:
                    tag = ensure_tag(db, tag_name)
                    if tag not in exercise.tags:
                        exercise.tags.append(tag)

                if not exercise.test_cases:
                    for ti, tc in enumerate(ex_def.get("test_cases", []) or []):
                        db.add(
                            TestCase(
                                exercise_id=exercise.id,
                                name=tc.get("name", f"case-{ti + 1}"),
                                stdin=tc.get("stdin", ""),
                                expected_stdout=tc.get("expected_stdout", ""),
                                is_hidden=tc.get("is_hidden", False),
                                weight=tc.get("weight", 1),
                                order_index=tc.get("order_index", ti),
                            )
                        )
                        stats["test_cases"] += 1

    return {"course": c["title"], **stats}


def main() -> None:
    parser = argparse.ArgumentParser(description="Import courses from seed/courses/.")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate all tables first.")
    args = parser.parse_args()

    if args.reset:
        print(">>> --reset: dropping all tables")
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    course_dirs = sorted(d for d in COURSES_DIR.iterdir() if (d / "course.yaml").exists())
    if not course_dirs:
        print(f"No courses found in {COURSES_DIR}")
        return

    print("=" * 64)
    print(f"  Importing {len(course_dirs)} course(s) from {COURSES_DIR}")
    print("=" * 64)

    with SessionLocal() as db:
        ensure_admin(db)
        totals = {"modules": 0, "lessons": 0, "exercises": 0, "test_cases": 0}
        for d in course_dirs:
            try:
                result = import_course(db, d)
            except Exception as exc:  # noqa: BLE001
                db.rollback()
                print(f"  FAILED {d.name}: {exc}")
                raise
            for k in totals:
                totals[k] += result[k]
            print(
                f"  + {result['course']:<34} "
                f"{result['modules']:>2} mod  {result['lessons']:>3} les  "
                f"{result['exercises']:>3} ex  {result['test_cases']:>3} tc"
            )
        db.commit()

    print("-" * 64)
    print(
        f"  TOTAL: {totals['modules']} modules, {totals['lessons']} lessons, "
        f"{totals['exercises']} exercises, {totals['test_cases']} test cases"
    )
    print("  Done.")


if __name__ == "__main__":
    main()
