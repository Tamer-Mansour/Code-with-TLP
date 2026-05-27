from pydantic import BaseModel, ConfigDict


# ── Public question (no correct answer leaked) ──
class QuizQuestionPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    lesson_id: int
    prompt: str
    options: list[str]
    order_index: int


# ── Submitting answers ──
class QuizAnswerSubmit(BaseModel):
    question_id: int
    selected_index: int


class QuizSubmit(BaseModel):
    answers: list[QuizAnswerSubmit]


# ── Grading results ──
class QuizQuestionResult(BaseModel):
    question_id: int
    selected_index: int
    correct_index: int
    is_correct: bool
    explanation: str | None = None


class QuizResult(BaseModel):
    total: int
    correct: int
    passed: bool  # all questions answered correctly
    results: list[QuizQuestionResult]


# ── Reviewing previously stored answers ──
class QuizAnswerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    question_id: int
    selected_index: int
    is_correct: bool


# ── Admin create/update ──
class QuizQuestionCreate(BaseModel):
    lesson_id: int
    prompt: str
    options: list[str]
    correct_index: int
    explanation: str | None = None
    order_index: int = 0
