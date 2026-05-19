from pydantic import BaseModel, ConfigDict, Field

from app.models.catalog import LessonType


# ---------- Subject ----------

class SubjectBase(BaseModel):
    name: str = Field(max_length=128)
    slug: str = Field(max_length=128)
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    order_index: int = 0


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    order_index: int | None = None


class SubjectRead(SubjectBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Course ----------

class CourseBase(BaseModel):
    subject_id: int
    title: str
    slug: str
    summary: str | None = None
    description: str | None = None
    cover_image: str | None = None
    difficulty: str = "beginner"
    estimated_hours: int = 0
    is_published: bool = False
    order_index: int = 0


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    subject_id: int | None = None
    title: str | None = None
    slug: str | None = None
    summary: str | None = None
    description: str | None = None
    cover_image: str | None = None
    difficulty: str | None = None
    estimated_hours: int | None = None
    is_published: bool | None = None
    order_index: int | None = None


class CourseRead(CourseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Module ----------

class ModuleBase(BaseModel):
    course_id: int
    title: str
    summary: str | None = None
    order_index: int = 0


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(BaseModel):
    title: str | None = None
    summary: str | None = None
    order_index: int | None = None


class ModuleRead(ModuleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Lesson ----------

class LessonBase(BaseModel):
    module_id: int
    title: str
    slug: str
    lesson_type: LessonType = LessonType.reading
    content_md: str | None = None
    video_url: str | None = None
    duration_minutes: int = 0
    order_index: int = 0


class LessonCreate(LessonBase):
    pass


class LessonUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    lesson_type: LessonType | None = None
    content_md: str | None = None
    video_url: str | None = None
    duration_minutes: int | None = None
    order_index: int | None = None


class LessonRead(LessonBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Course tree (nested view) ----------

class LessonInTree(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    lesson_type: LessonType
    duration_minutes: int
    order_index: int


class ModuleInTree(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    summary: str | None
    order_index: int
    lessons: list[LessonInTree]


class CourseTree(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    summary: str | None
    description: str | None
    difficulty: str
    estimated_hours: int
    modules: list[ModuleInTree]


# ---------- Tag ----------

class TagBase(BaseModel):
    name: str
    slug: str


class TagCreate(TagBase):
    pass


class TagRead(TagBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Learning Path ----------

class LearningPathBase(BaseModel):
    title: str
    slug: str
    description: str | None = None
    cover_image: str | None = None
    is_published: bool = False


class LearningPathCreate(LearningPathBase):
    course_ids: list[int] = []


class LearningPathUpdate(BaseModel):
    title: str | None = None
    slug: str | None = None
    description: str | None = None
    cover_image: str | None = None
    is_published: bool | None = None
    course_ids: list[int] | None = None


class LearningPathRead(LearningPathBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    courses: list[CourseRead] = []
