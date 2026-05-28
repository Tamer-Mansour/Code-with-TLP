from pydantic import BaseModel, ConfigDict


class InterviewQuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: int
    question: str
    answer: str
    difficulty: str
    tags: list[str] = []
    order_index: int


class InterviewCategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    order_index: int
    question_count: int = 0


class InterviewCategoryDetail(InterviewCategoryRead):
    questions: list[InterviewQuestionRead] = []
