from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.progress import ProgressStatus


class EnrollmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    course_id: int
    progress_percent: float
    completed_at: datetime | None
    created_at: datetime


class LessonProgressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    lesson_id: int
    status: ProgressStatus
    completed_at: datetime | None


class LessonProgressUpdate(BaseModel):
    status: ProgressStatus
