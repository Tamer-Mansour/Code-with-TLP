from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import (
    Course,
    Enrollment,
    Lesson,
    LessonProgress,
    Module,
    ProgressStatus,
    User,
)
from app.schemas.progress import EnrollmentRead, LessonProgressRead, LessonProgressUpdate

router = APIRouter(prefix="/progress", tags=["progress"])


def _recompute_course_progress(db: Session, user_id: int, course_id: int) -> Enrollment:
    enrollment = db.scalar(
        select(Enrollment).where(Enrollment.user_id == user_id, Enrollment.course_id == course_id)
    )
    if not enrollment:
        return None  # type: ignore[return-value]

    total_lessons = db.scalar(
        select(func.count(Lesson.id)).join(Module).where(Module.course_id == course_id)
    ) or 0
    completed = db.scalar(
        select(func.count(LessonProgress.id))
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .where(
            Module.course_id == course_id,
            LessonProgress.user_id == user_id,
            LessonProgress.status == ProgressStatus.completed,
        )
    ) or 0

    if total_lessons:
        enrollment.progress_percent = round((completed / total_lessons) * 100.0, 2)
    else:
        enrollment.progress_percent = 0.0
    if total_lessons and completed == total_lessons:
        enrollment.completed_at = datetime.now(timezone.utc)
    return enrollment


@router.post("/enroll/{course_id}", response_model=EnrollmentRead, status_code=201)
def enroll(course_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    existing = db.scalar(
        select(Enrollment).where(Enrollment.user_id == current.id, Enrollment.course_id == course_id)
    )
    if existing:
        return existing
    enrollment = Enrollment(user_id=current.id, course_id=course_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment


@router.delete("/enroll/{course_id}", status_code=204)
def unenroll(course_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    existing = db.scalar(
        select(Enrollment).where(Enrollment.user_id == current.id, Enrollment.course_id == course_id)
    )
    if not existing:
        raise HTTPException(status_code=404, detail="Not enrolled")
    db.delete(existing)
    db.commit()


@router.get("/enrollments", response_model=list[EnrollmentRead])
def my_enrollments(db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    return db.scalars(select(Enrollment).where(Enrollment.user_id == current.id)).all()


@router.get("/lessons/{lesson_id}", response_model=LessonProgressRead)
def lesson_progress(lesson_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    lp = db.scalar(
        select(LessonProgress).where(LessonProgress.user_id == current.id, LessonProgress.lesson_id == lesson_id)
    )
    if not lp:
        # Return a virtual not_started record without persisting.
        return LessonProgressRead(
            id=0,
            user_id=current.id,
            lesson_id=lesson_id,
            status=ProgressStatus.not_started,
            completed_at=None,
        )
    return lp


@router.put("/lessons/{lesson_id}", response_model=LessonProgressRead)
def set_lesson_progress(
    lesson_id: int,
    payload: LessonProgressUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    lesson = db.scalar(select(Lesson).where(Lesson.id == lesson_id))
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")

    lp = db.scalar(
        select(LessonProgress).where(LessonProgress.user_id == current.id, LessonProgress.lesson_id == lesson_id)
    )
    if not lp:
        lp = LessonProgress(user_id=current.id, lesson_id=lesson_id, status=payload.status)
        db.add(lp)
    else:
        lp.status = payload.status

    lp.completed_at = datetime.now(timezone.utc) if payload.status == ProgressStatus.completed else None

    # Flush so the recompute SELECT sees the change (session has autoflush=False).
    db.flush()

    # Keep the course-level enrollment progress in sync.
    module = db.get(Module, lesson.module_id)
    if module:
        _recompute_course_progress(db, current.id, module.course_id)

    db.commit()
    db.refresh(lp)
    return lp


@router.get("/course/{course_id}/lessons", response_model=list[LessonProgressRead])
def course_lesson_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """All lesson progress records for the current user in a given course."""
    return db.scalars(
        select(LessonProgress)
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .join(Module, Module.id == Lesson.module_id)
        .where(
            Module.course_id == course_id,
            LessonProgress.user_id == current.id,
        )
    ).all()
