# Studying App — Backend

FastAPI + SQLite + Docker-sandboxed code execution. Supports Python, JavaScript, TypeScript, Java, and C# exercises.

## Stack

- **FastAPI** + **Uvicorn**
- **SQLAlchemy 2.0** with SQLite (set `DATABASE_URL` to use Postgres/MySQL later)
- **JWT** auth (access + refresh tokens) with bcrypt password hashing
- **Docker** for per-submission code sandboxing
- Domain: subjects → courses → modules → lessons → exercises → test cases, plus enrollments, lesson progress, submissions, learning paths, tags

## Layout

```
backend/
├── app/
│   ├── main.py                # FastAPI entrypoint
│   ├── seed.py                # Seed admin + sample course/exercise
│   ├── core/                  # config, db, security
│   ├── models/                # SQLAlchemy models
│   ├── schemas/               # Pydantic request/response schemas
│   ├── api/
│   │   ├── deps.py            # auth dependencies
│   │   └── routes/            # auth, users, catalog, submissions, progress, admin
│   └── services/
│       ├── code_runner.py     # Docker-backed runner
│       └── judge.py           # Score a submission against test cases
└── docker/runners/            # One Dockerfile per supported language
```

## Setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env — at minimum set SECRET_KEY and FIRST_ADMIN_PASSWORD.
```

## Build the code-runner images

You need **Docker Desktop running** (Linux containers).

```powershell
.\docker\runners\build-all.ps1
```

(or `./docker/runners/build-all.sh` on Linux/macOS)

This produces:
- `studying-runner-python:latest`
- `studying-runner-node:latest`
- `studying-runner-java:latest`
- `studying-runner-csharp:latest`

## Seed the database

```powershell
python -m app.seed
```

Creates the admin user from `.env` and a "Sum two numbers" sample exercise wired to an Algorithms course.

## Run the API

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger UI:  http://localhost:8000/docs
- Health:      http://localhost:8000/health
- API prefix:  `/api/v1`

## Key endpoints

### Auth

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/v1/auth/register` | Register a student |
| POST | `/api/v1/auth/login` | Login with email or username |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET  | `/api/v1/auth/me` | Current user |

### Catalog (public reads)

- `GET /api/v1/catalog/subjects`
- `GET /api/v1/catalog/courses`
- `GET /api/v1/catalog/courses/{slug}` — full tree (modules + lessons)
- `GET /api/v1/catalog/lessons/{id}`
- `GET /api/v1/catalog/exercises` (filter by `difficulty`, `language`, `tag`, `q`)
- `GET /api/v1/catalog/exercises/{slug}` — student detail (no solution, no hidden cases)
- `GET /api/v1/catalog/learning-paths`

### Student progress

- `POST /api/v1/progress/enroll/{course_id}`
- `GET  /api/v1/progress/enrollments`
- `PUT  /api/v1/progress/lessons/{lesson_id}` — mark lesson `in_progress`/`completed`

### Code execution

- `POST /api/v1/submissions/run` — ad-hoc run with custom stdin (no grading)
- `POST /api/v1/submissions` — submit code → judged → scored → returns full results
- `GET  /api/v1/submissions/me` — your submission history
- `GET  /api/v1/submissions/{id}`

### Admin (role = admin only)

Mounted under `/api/v1/admin/...` — full CRUD over users, subjects (via `/catalog/subjects`), courses, modules, lessons, exercises, test cases. Plus:

- `GET /api/v1/admin/stats` — dashboard counters
- `GET /api/v1/admin/users` (filter `role`, `q`)
- `GET /api/v1/admin/submissions` (filter `user_id`, `exercise_id`, `status`)

## Notes on the judge

- Each submission runs once **per test case** inside a fresh container.
- Container limits: no network (`--network none`), capped memory (defaults to 256 MB), capped CPU (0.5 vCPU), `--pids-limit 128`, `no-new-privileges`.
- Wall-clock timeout = exercise `time_limit_ms` + 1s safety. Status `time_limit_exceeded` if exceeded.
- Output comparison is whitespace-tolerant (trailing whitespace per line is ignored).
- Hidden test cases are graded but their stdin/stdout aren't echoed back to the user.
- If a runner image is missing, the submission gets `status=internal_error` with a clear message — build the images.

## Next steps (frontend)

The Angular frontend will live in `frontend/` and consume `/api/v1/...`. Plan:

- `/login`, `/register` — auth flow with JWT in `Authorization: Bearer …`
- `/catalog`, `/courses/:slug`, `/lessons/:id` — student experience
- `/exercises/:slug` — Monaco editor + Run + Submit, results panel below
- `/dashboard` — enrollments, recent submissions, score totals
- `/admin/*` — guarded by `role === 'admin'`, CRUD pages for everything in the admin router

Hit `/health` first to confirm the API + Docker runner are wired up before building the UI.
