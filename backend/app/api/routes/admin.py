from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_admin
from app.core.database import get_db
from app.core.security import hash_password
from app.models import (
    Course,
    Exercise,
    Lesson,
    Module,
    Subject,
    Submission,
    Tag,
    TestCase,
    User,
)
from app.models.submission import SubmissionStatus
from app.models.user import UserRole
from app.schemas.admin import AdminStats
from app.schemas.catalog import (
    CourseCreate,
    CourseRead,
    CourseUpdate,
    LessonCreate,
    LessonRead,
    LessonUpdate,
    ModuleCreate,
    ModuleRead,
    ModuleUpdate,
)
from app.schemas.exercise import (
    ExerciseAdminRead,
    ExerciseCreate,
    ExerciseUpdate,
    TestCaseCreate,
    TestCaseRead,
    TestCaseUpdate,
)
from app.schemas.submission import SubmissionSummary
from app.schemas.user import UserAdminUpdate, UserCreate, UserRead

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_current_admin)])


# ---------- Dashboard ----------


@router.get("/stats", response_model=AdminStats)
def stats(db: Session = Depends(get_db)) -> AdminStats:
    def count(stmt):
        return db.scalar(stmt) or 0

    return AdminStats(
        users_total=count(select(func.count(User.id))),
        users_active=count(select(func.count(User.id)).where(User.is_active.is_(True))),
        students=count(select(func.count(User.id)).where(User.role == UserRole.student)),
        admins=count(select(func.count(User.id)).where(User.role == UserRole.admin)),
        subjects=count(select(func.count(Subject.id))),
        courses=count(select(func.count(Course.id))),
        courses_published=count(select(func.count(Course.id)).where(Course.is_published.is_(True))),
        lessons=count(select(func.count(Lesson.id))),
        exercises=count(select(func.count(Exercise.id))),
        exercises_published=count(select(func.count(Exercise.id)).where(Exercise.is_published.is_(True))),
        submissions=count(select(func.count(Submission.id))),
        submissions_accepted=count(
            select(func.count(Submission.id)).where(Submission.status == SubmissionStatus.accepted)
        ),
    )


# ---------- Users ----------


@router.get("/users", response_model=list[UserRead])
def list_users(
    db: Session = Depends(get_db),
    role: UserRole | None = None,
    q: str | None = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
):
    stmt = select(User)
    if role:
        stmt = stmt.where(User.role == role)
    if q:
        like = f"%{q.lower()}%"
        stmt = stmt.where(User.email.ilike(like) | User.username.ilike(like))
    return db.scalars(stmt.order_by(User.id).offset(offset).limit(limit)).all()


@router.post("/users", response_model=UserRead, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    if db.scalar(select(User).where((User.email == payload.email) | (User.username == payload.username))):
        raise HTTPException(status_code=409, detail="Email or username already taken")
    user = User(
        email=payload.email,
        username=payload.username,
        full_name=payload.full_name,
        avatar_url=payload.avatar_url,
        bio=payload.bio,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserAdminUpdate, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = payload.model_dump(exclude_unset=True)
    if "password" in data:
        password = data.pop("password")
        if password:
            user.hashed_password = hash_password(password)
    for k, v in data.items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()


# ---------- Courses ----------


@router.get("/courses", response_model=list[CourseRead])
def list_courses_admin(db: Session = Depends(get_db)):
    return db.scalars(select(Course).order_by(Course.id)).all()


@router.post("/courses", response_model=CourseRead, status_code=201)
def create_course(payload: CourseCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Course).where(Course.slug == payload.slug)):
        raise HTTPException(status_code=409, detail="Slug already taken")
    course = Course(**payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.patch("/courses/{course_id}", response_model=CourseRead)
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(course, k, v)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/courses/{course_id}", status_code=204)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    db.delete(course)
    db.commit()


# ---------- Modules ----------


@router.post("/modules", response_model=ModuleRead, status_code=201)
def create_module(payload: ModuleCreate, db: Session = Depends(get_db)):
    if not db.get(Course, payload.course_id):
        raise HTTPException(status_code=404, detail="Course not found")
    module = Module(**payload.model_dump())
    db.add(module)
    db.commit()
    db.refresh(module)
    return module


@router.patch("/modules/{module_id}", response_model=ModuleRead)
def update_module(module_id: int, payload: ModuleUpdate, db: Session = Depends(get_db)):
    module = db.get(Module, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(module, k, v)
    db.commit()
    db.refresh(module)
    return module


@router.delete("/modules/{module_id}", status_code=204)
def delete_module(module_id: int, db: Session = Depends(get_db)):
    module = db.get(Module, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    db.delete(module)
    db.commit()


# ---------- Lessons ----------


@router.post("/lessons", response_model=LessonRead, status_code=201)
def create_lesson(payload: LessonCreate, db: Session = Depends(get_db)):
    if not db.get(Module, payload.module_id):
        raise HTTPException(status_code=404, detail="Module not found")
    lesson = Lesson(**payload.model_dump())
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.patch("/lessons/{lesson_id}", response_model=LessonRead)
def update_lesson(lesson_id: int, payload: LessonUpdate, db: Session = Depends(get_db)):
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(lesson, k, v)
    db.commit()
    db.refresh(lesson)
    return lesson


@router.delete("/lessons/{lesson_id}", status_code=204)
def delete_lesson(lesson_id: int, db: Session = Depends(get_db)):
    lesson = db.get(Lesson, lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    db.delete(lesson)
    db.commit()


# ---------- Exercises ----------


@router.get("/exercises", response_model=list[ExerciseAdminRead])
def list_exercises_admin(db: Session = Depends(get_db)):
    return db.scalars(select(Exercise).options(selectinload(Exercise.test_cases)).order_by(Exercise.id)).all()


@router.get("/exercises/{exercise_id}", response_model=ExerciseAdminRead)
def get_exercise_admin(exercise_id: int, db: Session = Depends(get_db)):
    exercise = db.scalar(
        select(Exercise).where(Exercise.id == exercise_id).options(selectinload(Exercise.test_cases))
    )
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise


@router.post("/exercises", response_model=ExerciseAdminRead, status_code=201)
def create_exercise(payload: ExerciseCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Exercise).where(Exercise.slug == payload.slug)):
        raise HTTPException(status_code=409, detail="Slug already taken")
    data = payload.model_dump(exclude={"test_cases", "tag_ids"})
    exercise = Exercise(**data)
    if payload.tag_ids:
        exercise.tags = db.scalars(select(Tag).where(Tag.id.in_(payload.tag_ids))).all()
    for tc in payload.test_cases:
        exercise.test_cases.append(TestCase(**tc.model_dump()))
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


@router.patch("/exercises/{exercise_id}", response_model=ExerciseAdminRead)
def update_exercise(exercise_id: int, payload: ExerciseUpdate, db: Session = Depends(get_db)):
    exercise = db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    data = payload.model_dump(exclude_unset=True)
    tag_ids = data.pop("tag_ids", None)
    for k, v in data.items():
        setattr(exercise, k, v)
    if tag_ids is not None:
        exercise.tags = db.scalars(select(Tag).where(Tag.id.in_(tag_ids))).all()
    db.commit()
    db.refresh(exercise)
    return exercise


@router.delete("/exercises/{exercise_id}", status_code=204)
def delete_exercise(exercise_id: int, db: Session = Depends(get_db)):
    exercise = db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    db.delete(exercise)
    db.commit()


# ---------- Test cases ----------


@router.post("/exercises/{exercise_id}/test-cases", response_model=TestCaseRead, status_code=201)
def add_test_case(exercise_id: int, payload: TestCaseCreate, db: Session = Depends(get_db)):
    if not db.get(Exercise, exercise_id):
        raise HTTPException(status_code=404, detail="Exercise not found")
    tc = TestCase(exercise_id=exercise_id, **payload.model_dump())
    db.add(tc)
    db.commit()
    db.refresh(tc)
    return tc


@router.patch("/test-cases/{tc_id}", response_model=TestCaseRead)
def update_test_case(tc_id: int, payload: TestCaseUpdate, db: Session = Depends(get_db)):
    tc = db.get(TestCase, tc_id)
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(tc, k, v)
    db.commit()
    db.refresh(tc)
    return tc


@router.delete("/test-cases/{tc_id}", status_code=204)
def delete_test_case(tc_id: int, db: Session = Depends(get_db)):
    tc = db.get(TestCase, tc_id)
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")
    db.delete(tc)
    db.commit()


# ---------- Submissions browser ----------


@router.get("/submissions", response_model=list[SubmissionSummary])
def list_submissions(
    db: Session = Depends(get_db),
    user_id: int | None = None,
    exercise_id: int | None = None,
    status_filter: SubmissionStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, le=200),
    offset: int = 0,
):
    stmt = select(Submission)
    if user_id:
        stmt = stmt.where(Submission.user_id == user_id)
    if exercise_id:
        stmt = stmt.where(Submission.exercise_id == exercise_id)
    if status_filter:
        stmt = stmt.where(Submission.status == status_filter)
    return db.scalars(stmt.order_by(Submission.id.desc()).offset(offset).limit(limit)).all()
