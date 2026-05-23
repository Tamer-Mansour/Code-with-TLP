from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.submission import SubmissionStatus


SUPPORTED_LANGUAGES = {"python", "javascript", "typescript", "java", "csharp"}


class CodeRunRequest(BaseModel):
    """One-off 'Run code' request: execute against custom stdin, do not persist as a submission."""
    language: str
    code: str
    stdin: str = ""


class CodeRunResult(BaseModel):
    status: SubmissionStatus
    stdout: str = ""
    stderr: str = ""
    runtime_ms: int = 0
    memory_kb: int = 0
    error: str | None = None


class SubmissionCreate(BaseModel):
    exercise_id: int
    language: str
    code: str = Field(min_length=1)


class TestCaseResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    test_case_id: int
    passed: bool
    actual_stdout: str | None
    stderr: str | None
    runtime_ms: int
    error: str | None
    is_hidden: bool


class SubmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    exercise_id: int
    language: str
    code: str
    status: SubmissionStatus
    score: float
    passed_tests: int
    total_tests: int
    runtime_ms: int
    memory_kb: int
    stdout: str | None
    stderr: str | None
    error_message: str | None
    created_at: datetime
    results: list[TestCaseResultRead] = []


class SubmissionSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    exercise_id: int
    language: str
    code: str
    status: SubmissionStatus
    score: float
    passed_tests: int
    total_tests: int
    runtime_ms: int
    created_at: datetime
