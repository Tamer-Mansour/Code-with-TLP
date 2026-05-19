from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.models import (
    Course,
    Difficulty,
    Exercise,
    LearningPath,
    Lesson,
    Module,
    Subject,
    Tag,
    User,
)
from app.schemas.catalog import (
    CourseRead,
    CourseTree,
    LearningPathCreate,
    LearningPathRead,
    LearningPathUpdate,
    LessonRead,
    ModuleRead,
    SubjectCreate,
    SubjectRead,
    SubjectUpdate,
    TagCreate,
    TagRead,
)
from app.schemas.exercise import ExerciseRead, ExerciseSummary, TestCasePublic

router = APIRouter(prefix="/catalog", tags=["catalog"])


# ---------- Public reads ----------


@router.get("/subjects", response_model=list[SubjectRead])
def list_subjects(db: Session = Depends(get_db)):
    return db.scalars(select(Subject).order_by(Subject.order_index, Subject.name)).all()


@router.get("/subjects/{slug}", response_model=SubjectRead)
def get_subject(slug: str, db: Session = Depends(get_db)):
    subject = db.scalar(select(Subject).where(Subject.slug == slug))
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.get("/subjects/{slug}/courses", response_model=list[CourseRead])
def list_subject_courses(slug: str, db: Session = Depends(get_db)):
    subject = db.scalar(select(Subject).where(Subject.slug == slug))
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return (
        db.scalars(
            select(Course)
            .where(Course.subject_id == subject.id, Course.is_published.is_(True))
            .order_by(Course.order_index, Course.title)
        ).all()
    )


@router.get("/courses", response_model=list[CourseRead])
def list_courses(
    db: Session = Depends(get_db),
    subject_id: int | None = None,
    difficulty: str | None = None,
    q: str | None = None,
):
    stmt = select(Course).where(Course.is_published.is_(True))
    if subject_id is not None:
        stmt = stmt.where(Course.subject_id == subject_id)
    if difficulty:
        stmt = stmt.where(Course.difficulty == difficulty)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(Course.title.ilike(like) | Course.summary.ilike(like))
    stmt = stmt.order_by(Course.order_index, Course.title)
    return db.scalars(stmt).all()


@router.get("/courses/{slug}", response_model=CourseTree)
def get_course_tree(slug: str, db: Session = Depends(get_db)):
    course = db.scalar(
        select(Course)
        .where(Course.slug == slug)
        .options(selectinload(Course.modules).selectinload(Module.lessons))
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.get("/lessons/{lesson_id}", response_model=LessonRead)
def get_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return lesson


@router.get("/lessons/{lesson_id}/exercises", response_model=list[ExerciseSummary])
def list_lesson_exercises(lesson_id: int, db: Session = Depends(get_db)):
    return db.scalars(
        select(Exercise).where(Exercise.lesson_id == lesson_id, Exercise.is_published.is_(True))
    ).all()


@router.get("/exercises", response_model=list[ExerciseSummary])
def list_exercises(
    db: Session = Depends(get_db),
    difficulty: Difficulty | None = None,
    language: str | None = None,
    tag: str | None = None,
    q: str | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
):
    stmt = select(Exercise).where(Exercise.is_published.is_(True))
    if difficulty:
        stmt = stmt.where(Exercise.difficulty == difficulty)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(Exercise.title.ilike(like))
    if tag:
        stmt = stmt.join(Exercise.tags).where(Tag.slug == tag)
    rows = db.scalars(stmt.order_by(Exercise.id).offset(offset).limit(limit)).all()
    if language:
        rows = [e for e in rows if language in (e.supported_languages or [])]
    return rows


@router.get("/exercises/{slug}", response_model=ExerciseRead)
def get_exercise(slug: str, db: Session = Depends(get_db)):
    exercise = db.scalar(
        select(Exercise)
        .where(Exercise.slug == slug, Exercise.is_published.is_(True))
        .options(selectinload(Exercise.test_cases))
    )
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    # Student-facing detail must not leak solution code or hidden test cases.
    safe_test_cases = [TestCasePublic.model_validate(tc) for tc in exercise.test_cases if not tc.is_hidden]
    data = ExerciseRead.model_validate(exercise).model_copy(update={"test_cases": safe_test_cases, "solution_code": {}})
    return data


@router.get("/learning-paths", response_model=list[LearningPathRead])
def list_learning_paths(db: Session = Depends(get_db)):
    return db.scalars(
        select(LearningPath)
        .where(LearningPath.is_published.is_(True))
        .options(selectinload(LearningPath.courses))
    ).all()


@router.get("/learning-paths/{slug}", response_model=LearningPathRead)
def get_learning_path(slug: str, db: Session = Depends(get_db)):
    path = db.scalar(
        select(LearningPath).where(LearningPath.slug == slug).options(selectinload(LearningPath.courses))
    )
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return path


# ---------- Admin writes ----------


@router.post("/subjects", response_model=SubjectRead, status_code=201)
def create_subject(payload: SubjectCreate, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    if db.scalar(select(Subject).where(Subject.slug == payload.slug)):
        raise HTTPException(status_code=409, detail="Slug already taken")
    subject = Subject(**payload.model_dump())
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


@router.patch("/subjects/{subject_id}", response_model=SubjectRead)
def update_subject(
    subject_id: int,
    payload: SubjectUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(subject, k, v)
    db.commit()
    db.refresh(subject)
    return subject


@router.delete("/subjects/{subject_id}", status_code=204)
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    subject = db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    db.delete(subject)
    db.commit()


# Tags

@router.get("/tags", response_model=list[TagRead])
def list_tags(db: Session = Depends(get_db)):
    return db.scalars(select(Tag).order_by(Tag.name)).all()


@router.post("/tags", response_model=TagRead, status_code=201)
def create_tag(payload: TagCreate, db: Session = Depends(get_db), _: User = Depends(get_current_admin)):
    if db.scalar(select(Tag).where(Tag.slug == payload.slug)):
        raise HTTPException(status_code=409, detail="Slug already taken")
    tag = Tag(**payload.model_dump())
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


# Learning paths (admin)

@router.post("/learning-paths", response_model=LearningPathRead, status_code=201)
def create_learning_path(
    payload: LearningPathCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    if db.scalar(select(LearningPath).where(LearningPath.slug == payload.slug)):
        raise HTTPException(status_code=409, detail="Slug already taken")
    data = payload.model_dump(exclude={"course_ids"})
    path = LearningPath(**data)
    if payload.course_ids:
        path.courses = db.scalars(select(Course).where(Course.id.in_(payload.course_ids))).all()
    db.add(path)
    db.commit()
    db.refresh(path)
    return path


@router.patch("/learning-paths/{path_id}", response_model=LearningPathRead)
def update_learning_path(
    path_id: int,
    payload: LearningPathUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
):
    path = db.get(LearningPath, path_id)
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    data = payload.model_dump(exclude_unset=True)
    course_ids = data.pop("course_ids", None)
    for k, v in data.items():
        setattr(path, k, v)
    if course_ids is not None:
        path.courses = db.scalars(select(Course).where(Course.id.in_(course_ids))).all()
    db.commit()
    db.refresh(path)
    return path
