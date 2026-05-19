from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Exercise, ProgressStatus, Submission, User
from app.models.progress import LessonProgress
from app.models.submission import SubmissionStatus
from app.schemas.submission import (
    SUPPORTED_LANGUAGES,
    CodeRunRequest,
    CodeRunResult,
    SubmissionCreate,
    SubmissionRead,
    SubmissionSummary,
)
from app.services.code_runner import code_runner
from app.services.judge import grade_submission

router = APIRouter(prefix="/submissions", tags=["submissions"])


def _ensure_language(language: str, exercise: Exercise | None = None) -> None:
    if language not in SUPPORTED_LANGUAGES:
        raise HTTPException(status_code=400, detail=f"Unsupported language: {language}")
    if exercise and exercise.supported_languages and language not in exercise.supported_languages:
        raise HTTPException(status_code=400, detail=f"Language not enabled for this exercise: {language}")


@router.post("/run", response_model=CodeRunResult)
def run_code(payload: CodeRunRequest, _: User = Depends(get_current_user)) -> CodeRunResult:
    """Ad-hoc 'Run' button — execute code with custom stdin, no scoring, no persistence."""
    _ensure_language(payload.language)
    result = code_runner.run(language=payload.language, code=payload.code, stdin=payload.stdin)
    status = (
        SubmissionStatus.internal_error
        if result.error
        else SubmissionStatus.time_limit_exceeded
        if result.timed_out
        else SubmissionStatus.memory_limit_exceeded
        if result.out_of_memory
        else SubmissionStatus.runtime_error
        if result.exit_code != 0
        else SubmissionStatus.accepted
    )
    return CodeRunResult(
        status=status,
        stdout=result.stdout,
        stderr=result.stderr,
        runtime_ms=result.runtime_ms,
        memory_kb=0,
        error=result.error,
    )


@router.post("", response_model=SubmissionRead, status_code=201)
def submit(
    payload: SubmissionCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> Submission:
    exercise = db.scalar(
        select(Exercise).where(Exercise.id == payload.exercise_id).options(selectinload(Exercise.test_cases))
    )
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    if not exercise.is_published:
        raise HTTPException(status_code=403, detail="Exercise is not published")

    _ensure_language(payload.language, exercise)

    submission = Submission(
        user_id=current.id,
        exercise_id=exercise.id,
        language=payload.language,
        code=payload.code,
    )
    db.add(submission)
    db.flush()  # get an id

    grade_submission(db, submission, exercise)

    # If accepted and tied to a lesson, mark that lesson as completed for this user.
    if submission.status == SubmissionStatus.accepted and exercise.lesson_id:
        progress = db.scalar(
            select(LessonProgress).where(
                LessonProgress.user_id == current.id,
                LessonProgress.lesson_id == exercise.lesson_id,
            )
        )
        if not progress:
            progress = LessonProgress(
                user_id=current.id,
                lesson_id=exercise.lesson_id,
                status=ProgressStatus.completed,
                completed_at=datetime.now(timezone.utc),
            )
            db.add(progress)
        else:
            progress.status = ProgressStatus.completed
            progress.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(submission)
    return submission


@router.get("/me", response_model=list[SubmissionSummary])
def my_submissions(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
    exercise_id: int | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
):
    stmt = select(Submission).where(Submission.user_id == current.id)
    if exercise_id:
        stmt = stmt.where(Submission.exercise_id == exercise_id)
    stmt = stmt.order_by(Submission.id.desc()).offset(offset).limit(limit)
    return db.scalars(stmt).all()


@router.get("/{submission_id}", response_model=SubmissionRead)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> Submission:
    submission = db.scalar(
        select(Submission).where(Submission.id == submission_id).options(selectinload(Submission.results))
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if submission.user_id != current.id and current.role.value != "admin":
        raise HTTPException(status_code=403, detail="Not allowed")
    return submission
