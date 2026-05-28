"""Interview prep — public Q&A browsing + search. No auth required."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.interview import InterviewCategory, InterviewQuestion
from app.schemas.interview import (
    InterviewCategoryDetail,
    InterviewCategoryRead,
    InterviewQuestionRead,
)

router = APIRouter(prefix="/interview", tags=["interview"])


def _category_read(cat: InterviewCategory, count: int) -> InterviewCategoryRead:
    return InterviewCategoryRead(
        id=cat.id, name=cat.name, slug=cat.slug, description=cat.description,
        icon=cat.icon, color=cat.color, order_index=cat.order_index, question_count=count,
    )


@router.get("/categories", response_model=list[InterviewCategoryRead])
def list_categories(db: Session = Depends(get_db)):
    cats = db.scalars(select(InterviewCategory).order_by(InterviewCategory.order_index, InterviewCategory.name)).all()
    counts = dict(
        db.execute(
            select(InterviewQuestion.category_id, func.count(InterviewQuestion.id))
            .group_by(InterviewQuestion.category_id)
        ).all()
    )
    return [_category_read(c, counts.get(c.id, 0)) for c in cats]


@router.get("/categories/{slug}", response_model=InterviewCategoryDetail)
def get_category(slug: str, db: Session = Depends(get_db)):
    cat = db.scalar(select(InterviewCategory).where(InterviewCategory.slug == slug))
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    detail = InterviewCategoryDetail.model_validate(cat)
    detail.question_count = len(cat.questions)
    return detail


@router.get("/questions", response_model=list[InterviewQuestionRead])
def search_questions(
    db: Session = Depends(get_db),
    q: str | None = None,
    category: str | None = None,
    difficulty: str | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
):
    stmt = select(InterviewQuestion)
    if category:
        stmt = stmt.join(InterviewCategory).where(InterviewCategory.slug == category)
    if difficulty:
        stmt = stmt.where(InterviewQuestion.difficulty == difficulty)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(InterviewQuestion.question).like(like),
                func.lower(InterviewQuestion.answer).like(like),
            )
        )
    stmt = stmt.order_by(InterviewQuestion.category_id, InterviewQuestion.order_index).offset(offset).limit(limit)
    return db.scalars(stmt).all()


@router.get("/questions/{question_id}", response_model=InterviewQuestionRead)
def get_question(question_id: int, db: Session = Depends(get_db)):
    qrow = db.get(InterviewQuestion, question_id)
    if not qrow:
        raise HTTPException(status_code=404, detail="Question not found")
    return qrow
