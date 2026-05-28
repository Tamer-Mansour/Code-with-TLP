"""Load interview Q&A from backend/seed/interview/*.json into the DB.

Each JSON file is one category. Idempotent — rebuilds a category's questions on
every run. Run from backend/:  python seed/import_interview.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import delete, select  # noqa: E402

from app.core.database import SessionLocal, engine  # noqa: E402
from app.models import Base, InterviewCategory, InterviewQuestion  # noqa: E402

DIR = Path(__file__).resolve().parent / "interview"


def run() -> None:
    Base.metadata.create_all(bind=engine)
    files = sorted(p for p in DIR.glob("*.json"))
    if not files:
        print(f"No interview JSON files in {DIR}")
        return

    with SessionLocal() as db:
        total_q = 0
        print("=" * 56)
        for f in files:
            data = json.loads(f.read_text(encoding="utf-8"))
            c = data["category"]
            cat = db.scalar(select(InterviewCategory).where(InterviewCategory.slug == c["slug"]))
            if cat:
                cat.name = c["name"]
                cat.description = c.get("description")
                cat.icon = c.get("icon")
                cat.color = c.get("color")
                cat.order_index = c.get("order_index", 0)
                db.execute(delete(InterviewQuestion).where(InterviewQuestion.category_id == cat.id))
                db.flush()
            else:
                cat = InterviewCategory(
                    name=c["name"], slug=c["slug"], description=c.get("description"),
                    icon=c.get("icon"), color=c.get("color"), order_index=c.get("order_index", 0),
                )
                db.add(cat)
                db.flush()

            qs = data.get("questions", [])
            for i, q in enumerate(qs):
                db.add(InterviewQuestion(
                    category_id=cat.id,
                    question=q["question"],
                    answer=q["answer"],
                    difficulty=q.get("difficulty", "medium"),
                    tags=q.get("tags", []),
                    order_index=q.get("order_index", i),
                ))
            total_q += len(qs)
            print(f"  {c['slug']:<30} {len(qs):>3} questions")

        db.commit()
        print("-" * 56)
        print(f"  Categories: {len(files)} | Questions: {total_q}")
        print("=" * 56)


if __name__ == "__main__":
    run()
