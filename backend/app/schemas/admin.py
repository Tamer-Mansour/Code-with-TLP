from pydantic import BaseModel


class AdminStats(BaseModel):
    users_total: int
    users_active: int
    students: int
    admins: int
    subjects: int
    courses: int
    courses_published: int
    lessons: int
    exercises: int
    exercises_published: int
    submissions: int
    submissions_accepted: int
