from pydantic import BaseModel, ConfigDict, Field

from app.models.exercise import Difficulty


class TestCaseBase(BaseModel):
    name: str | None = None
    stdin: str = ""
    expected_stdout: str = ""
    is_hidden: bool = False
    weight: int = 1
    order_index: int = 0


class TestCaseCreate(TestCaseBase):
    pass


class TestCaseUpdate(BaseModel):
    name: str | None = None
    stdin: str | None = None
    expected_stdout: str | None = None
    is_hidden: bool | None = None
    weight: int | None = None
    order_index: int | None = None


class TestCaseRead(TestCaseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    exercise_id: int


class TestCasePublic(BaseModel):
    """A test case as visible to a student (hidden test cases are filtered out before this is built)."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str | None
    stdin: str
    expected_stdout: str
    order_index: int


class ExerciseBase(BaseModel):
    lesson_id: int | None = None
    title: str
    slug: str
    prompt_md: str
    difficulty: Difficulty = Difficulty.easy
    is_published: bool = False
    starter_code: dict[str, str] = Field(default_factory=dict)
    solution_code: dict[str, str] = Field(default_factory=dict)
    supported_languages: list[str] = Field(default_factory=list)
    time_limit_ms: int = 2000
    memory_limit_mb: int = 256
    points: int = 10


class ExerciseCreate(ExerciseBase):
    test_cases: list[TestCaseCreate] = []
    tag_ids: list[int] = []


class ExerciseUpdate(BaseModel):
    lesson_id: int | None = None
    title: str | None = None
    slug: str | None = None
    prompt_md: str | None = None
    difficulty: Difficulty | None = None
    is_published: bool | None = None
    starter_code: dict[str, str] | None = None
    solution_code: dict[str, str] | None = None
    supported_languages: list[str] | None = None
    time_limit_ms: int | None = None
    memory_limit_mb: int | None = None
    points: int | None = None
    tag_ids: list[int] | None = None


class ExerciseSummary(BaseModel):
    """Light view for catalog listings."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    lesson_id: int | None = None
    title: str
    slug: str
    difficulty: Difficulty
    points: int
    supported_languages: list[str]
    course_slug: str | None = None
    course_title: str | None = None


class ExerciseRead(ExerciseBase):
    """Student-facing detail. Solution code is omitted at the route layer."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    test_cases: list[TestCasePublic] = []


class ExerciseAdminRead(ExerciseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    test_cases: list[TestCaseRead] = []
