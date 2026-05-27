"""Parse quiz-type lessons' markdown into the quiz_questions table.

Lesson quiz markdown uses the convention:

    **Q1. Which is fastest to access?**
    - [ ] Main memory
    - [x] L1 cache
    - [ ] SSD

Run from backend/:  python seed/parse_quizzes.py
Idempotent — rebuilds questions for every quiz lesson each run.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete, select  # noqa: E402

from app.core.database import SessionLocal, engine  # noqa: E402
from app.models import Base, Lesson, LessonType, QuizQuestion  # noqa: E402

OPTION_RE = re.compile(r'^\s*[-*]\s*\[([ xX])\]\s*(.+?)\s*$')
BOLD_RE = re.compile(r'^\s*\*\*(.+?)\*\*\s*$')
QNUM_RE = re.compile(r'^(?:Q(?:uestion)?\s*\d+|\d+)\s*[\.\):]?\s*', re.IGNORECASE)
HEADING_RE = re.compile(r'^\s*#')


def parse_questions(md: str) -> list[dict]:
    questions: list[dict] = []
    current: dict | None = None

    def finalize():
        nonlocal current
        if current and len(current["options"]) >= 2 and current["correct_index"] >= 0:
            questions.append(current)
        current = None

    for raw in md.splitlines():
        opt = OPTION_RE.match(raw)
        if opt and current is not None:
            checked = opt.group(1).lower() == "x"
            text = opt.group(2).strip()
            if checked:
                current["correct_index"] = len(current["options"])
            current["options"].append(text)
            continue

        bold = BOLD_RE.match(raw)
        if bold:
            finalize()
            prompt = QNUM_RE.sub("", bold.group(1).strip()).strip()
            current = {"prompt": prompt, "options": [], "correct_index": -1}
            continue

        if HEADING_RE.match(raw):
            finalize()

    finalize()
    return questions


def run() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        quiz_lessons = db.scalars(
            select(Lesson).where(Lesson.lesson_type == LessonType.quiz)
        ).all()

        total_q = 0
        lessons_with_q = 0
        for lesson in quiz_lessons:
            if not lesson.content_md:
                continue
            parsed = parse_questions(lesson.content_md)
            if not parsed:
                continue
            # Rebuild this lesson's questions.
            db.execute(delete(QuizQuestion).where(QuizQuestion.lesson_id == lesson.id))
            for i, q in enumerate(parsed):
                db.add(QuizQuestion(
                    lesson_id=lesson.id,
                    prompt=q["prompt"],
                    options=q["options"],
                    correct_index=q["correct_index"],
                    order_index=i,
                ))
            total_q += len(parsed)
            lessons_with_q += 1

        db.commit()
        print(f"Quiz lessons scanned : {len(quiz_lessons)}")
        print(f"Lessons with questions: {lessons_with_q}")
        print(f"Questions created     : {total_q}")


if __name__ == "__main__":
    run()
