from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ── Canonical vocabularies (kept in sync with the frontend wizard) ───────────
INTERESTS = {"foundations", "web", "data", "algorithms", "ai", "systems", "mobile"}
LANGUAGES = {
    "python", "javascript", "typescript", "java", "csharp",
    "cpp", "c", "sql", "go", "rust", "php", "ruby", "kotlin", "swift",
}
GOALS = {"career", "school", "interview", "hobby", "upskill"}
LEVELS = {"new", "beginner", "intermediate", "advanced"}


class LearningProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    goal: str | None = None
    experience_level: str | None = None
    weekly_hours: int | None = None
    interests: list[str] = []
    languages: list[str] = []
    onboarded: bool
    created_at: datetime
    updated_at: datetime


class LearningProfileUpdate(BaseModel):
    goal: str | None = None
    experience_level: str | None = None
    weekly_hours: int | None = Field(default=None, ge=1, le=60)
    interests: list[str] | None = None
    languages: list[str] | None = None
    onboarded: bool | None = None

    @field_validator("goal")
    @classmethod
    def _check_goal(cls, v: str | None) -> str | None:
        if v is not None and v not in GOALS:
            raise ValueError(f"goal must be one of {sorted(GOALS)}")
        return v

    @field_validator("experience_level")
    @classmethod
    def _check_level(cls, v: str | None) -> str | None:
        if v is not None and v not in LEVELS:
            raise ValueError(f"experience_level must be one of {sorted(LEVELS)}")
        return v

    @field_validator("interests")
    @classmethod
    def _clean_interests(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        # Keep known interests, de-duplicate, preserve order.
        seen: list[str] = []
        for item in v:
            key = item.strip().lower()
            if key in INTERESTS and key not in seen:
                seen.append(key)
        return seen

    @field_validator("languages")
    @classmethod
    def _clean_languages(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        seen: list[str] = []
        for item in v:
            key = item.strip().lower()
            if key in LANGUAGES and key not in seen:
                seen.append(key)
        return seen
