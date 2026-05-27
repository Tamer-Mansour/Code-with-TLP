from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import ProgressStatus
from app.models.catalog import Lesson
from app.models.progress import LessonProgress
from app.models.quiz import QuizAnswer, QuizQuestion
from app.models.user import User
from app.schemas.quiz import (
    QuizAnswerRead,
    QuizQuestionPublic,
    QuizQuestionResult,
    QuizResult,
    QuizSubmit,
)

router = APIRouter(prefix="/quiz", tags=["quiz"])


def _questions_for(db: Session, lesson_id: int) -> list[QuizQuestion]:
    return list(
        db.scalars(
            select(QuizQuestion)
            .where(QuizQuestion.lesson_id == lesson_id)
            .order_by(QuizQuestion.order_index, QuizQuestion.id)
        ).all()
    )


@router.get("/lessons/{lesson_id}/questions", response_model=list[QuizQuestionPublic])
def get_quiz_questions(lesson_id: int, db: Session = Depends(get_db)):
    """Public quiz questions for a lesson — correct answers are NOT included."""
    return _questions_for(db, lesson_id)


@router.get("/lessons/{lesson_id}/my-answers", response_model=list[QuizAnswerRead])
def my_quiz_answers(
    lesson_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    q_ids = [q.id for q in _questions_for(db, lesson_id)]
    if not q_ids:
        return []
    return list(
        db.scalars(
            select(QuizAnswer).where(
                QuizAnswer.user_id == current.id,
                QuizAnswer.question_id.in_(q_ids),
            )
        ).all()
    )


@router.post("/lessons/{lesson_id}/submit", response_model=QuizResult)
def submit_quiz(
    lesson_id: int,
    payload: QuizSubmit,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    questions = _questions_for(db, lesson_id)
    if not questions:
        raise HTTPException(status_code=404, detail="This lesson has no quiz.")

    by_id = {q.id: q for q in questions}
    chosen = {a.question_id: a.selected_index for a in payload.answers}

    # Require every question to be answered before grading.
    missing = [q.id for q in questions if q.id not in chosen]
    if missing:
        raise HTTPException(status_code=400, detail="Answer all questions before submitting.")

    results: list[QuizQuestionResult] = []
    correct = 0
    for q in questions:
        sel = chosen[q.id]
        is_correct = sel == q.correct_index
        if is_correct:
            correct += 1

        # Upsert the user's stored answer.
        existing = db.scalar(
            select(QuizAnswer).where(
                QuizAnswer.user_id == current.id, QuizAnswer.question_id == q.id
            )
        )
        if existing:
            existing.selected_index = sel
            existing.is_correct = is_correct
        else:
            db.add(QuizAnswer(
                user_id=current.id,
                question_id=q.id,
                selected_index=sel,
                is_correct=is_correct,
            ))

        results.append(QuizQuestionResult(
            question_id=q.id,
            selected_index=sel,
            correct_index=q.correct_index,
            is_correct=is_correct,
            explanation=q.explanation,
        ))

    passed = correct == len(questions)

    # Mark the lesson completed when the learner gets everything right.
    if passed:
        prog = db.scalar(
            select(LessonProgress).where(
                LessonProgress.user_id == current.id,
                LessonProgress.lesson_id == lesson_id,
            )
        )
        if prog:
            prog.status = ProgressStatus.completed
            prog.completed_at = datetime.now(timezone.utc)
        else:
            db.add(LessonProgress(
                user_id=current.id,
                lesson_id=lesson_id,
                status=ProgressStatus.completed,
                completed_at=datetime.now(timezone.utc),
            ))

    db.commit()
    return QuizResult(total=len(questions), correct=correct, passed=passed, results=results)
