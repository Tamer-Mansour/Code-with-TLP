# Code with TLP — Backend

FastAPI + SQLite + Docker-sandboxed code execution.
Supports Python, JavaScript, TypeScript, Java, and C# exercises.

## Stack

- **FastAPI 0.115** + **Uvicorn** (hot-reload in dev via `--reload`)
- **SQLAlchemy 2.0** with SQLite — change `DATABASE_URL` in `.env` to switch to PostgreSQL
- **JWT** auth — access tokens (60 min) + refresh tokens (14 days), bcrypt password hashing
- **Docker** — one throwaway container per test case, hard-capped CPU / RAM / PIDs / network
- Domain model: subjects → courses → modules → lessons → exercises → test cases, plus enrollments, lesson progress, submissions, learning paths

## Layout

```
backend/
├── app/
│   ├── main.py                # App factory, CORS middleware, global exception handler
│   ├── seed.py                # Seed admin user + sample course/exercise
│   ├── core/
│   │   ├── config.py          # Pydantic settings (reads .env)
│   │   ├── database.py        # SQLAlchemy engine + session
│   │   └── security.py        # JWT helpers, bcrypt
│   ├── models/                # SQLAlchemy ORM models
│   ├── schemas/               # Pydantic request/response schemas
│   ├── api/
│   │   ├── deps.py            # get_current_user, get_db dependencies
│   │   └── routes/
│   │       ├── auth.py        # register, login, refresh, me
│   │       ├── users.py       # GET/PATCH /users/me
│   │       ├── catalog.py     # subjects, courses, lessons, exercises, learning paths
│   │       ├── submissions.py # run (ad-hoc), submit (graded), history
│   │       ├── progress.py    # enroll, lesson progress
│   │       └── admin.py       # admin-only CRUD + stats
│   └── services/
│       ├── code_runner.py     # Docker-backed sandbox runner
│       └── judge.py           # Score a submission against all test cases
├── docker/runners/            # One Dockerfile per supported language
│   ├── python/
│   ├── node/                  # JavaScript + TypeScript (tsx)
│   ├── java/
│   └── csharp/
├── tests/                     # ~69 pytest tests (Docker mocked)
├── Dockerfile
├── requirements.txt
└── .env.example
```

---

## Setup (using make from the repo root)

```powershell
make bootstrap    # create venv + copy .env + seed the database
make runners      # build the Docker sandbox images
make run          # start FastAPI on :8000 with hot reload
```

Or with the PowerShell wrapper:

```powershell
.\make.ps1 bootstrap
.\make.ps1 runners
.\make.ps1 run
```

### Manual setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env — set SECRET_KEY and FIRST_ADMIN_PASSWORD at minimum
python -m app.seed
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Swagger UI:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health
- **API prefix:** `/api/v1`

---

## Build the sandbox runner images

Docker Desktop must be running with Linux containers.

```powershell
.\docker\runners\build-all.ps1        # Windows
./docker/runners/build-all.sh         # Linux / macOS
# or from repo root:
make runners
```

This produces four images:

| Image | Languages |
|-------|-----------|
| `studying-runner-python:latest` | Python 3 |
| `studying-runner-node:latest` | JavaScript, TypeScript (tsx) |
| `studying-runner-java:latest` | Java |
| `studying-runner-csharp:latest` | C# (dotnet-script) |

If an image is missing, submissions using that language get `status = internal_error` with a clear message pointing to the build step.

---

## Environment variables (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `change-me` | JWT signing secret — **must be changed** |
| `DATABASE_URL` | `sqlite:///./studying_app.db` | SQLAlchemy connection string |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `14` | Refresh token lifetime |
| `FIRST_ADMIN_EMAIL` | `admin@studying.app` | Seeded admin email |
| `FIRST_ADMIN_USERNAME` | `admin` | Seeded admin username |
| `FIRST_ADMIN_PASSWORD` | `ChangeMe123!` | Seeded admin password — **change this** |
| `DOCKER_ENABLED` | `true` | Set to `false` to disable sandbox (submissions get `internal_error`) |
| `RUNNER_DEFAULT_TIMEOUT_SEC` | `5` | Max wall-clock time per test case |
| `RUNNER_DEFAULT_MEMORY_MB` | `256` | Container memory cap |
| `CORS_ORIGINS` | `http://localhost:4200` | Comma-separated allowed origins |

---

## API endpoints

### Auth

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/register` | — | Register a new student |
| POST | `/api/v1/auth/login` | — | Login, returns JWT pair |
| POST | `/api/v1/auth/refresh` | — | Refresh access token |
| GET  | `/api/v1/auth/me` | ✓ | Current user info |

### Users

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET    | `/api/v1/users/me` | ✓ | Current user profile |
| PATCH  | `/api/v1/users/me` | ✓ | Update name, bio, avatar, password |

### Catalog (public reads)

- `GET /api/v1/catalog/subjects`
- `GET /api/v1/catalog/courses` — filter by `q`, `difficulty`, `subject_id`
- `GET /api/v1/catalog/courses/{slug}` — full tree (modules + lessons)
- `GET /api/v1/catalog/lessons/{id}`
- `GET /api/v1/catalog/exercises` — filter by `difficulty`, `language`, `q`
- `GET /api/v1/catalog/exercises/{slug}` — student detail (no solution, hidden cases redacted)
- `GET /api/v1/catalog/learning-paths`

### Submissions

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/submissions/run` | ✓ | Ad-hoc run with custom stdin, no grading |
| POST | `/api/v1/submissions` | ✓ | Submit code → judged → scored |
| GET  | `/api/v1/submissions/me` | ✓ | Submission history (paginated) |
| GET  | `/api/v1/submissions/{id}` | ✓ | Full submission detail |

### Progress

- `POST /api/v1/progress/enroll/{course_id}` — enroll in a course
- `GET  /api/v1/progress/enrollments` — your enrollments
- `PUT  /api/v1/progress/lessons/{lesson_id}` — mark `in_progress` / `completed`

### Admin (role = admin only)

All under `/api/v1/admin/`:

- `GET /admin/stats` — platform counters
- `GET /admin/users` — filter by `role`, `q`
- `GET /admin/submissions` — filter by `user_id`, `exercise_id`, `status`
- Full CRUD over subjects, courses, modules, lessons, exercises, and test cases

---

## How the judge works

Each submission runs **once per test case** inside a fresh Docker container:

```
FastAPI → grade_submission() → code_runner.run() → Docker container
                                  ↑                     ↓
                           repeated per TC         stdout/stderr
```

Container constraints:

| Limit | Value |
|-------|-------|
| Network | `--network none` |
| Memory | 256 MB (configurable) |
| CPU | 0.5 vCPU |
| PIDs | 128 |
| Privileges | `no-new-privileges` |
| Timeout | exercise `time_limit_ms` + 1 s |

Output comparison is whitespace-tolerant (trailing whitespace per line is stripped before comparing).

---

## Running the tests

```powershell
make test        # ~69 tests
make test-cov    # with coverage report
```

Docker is **mocked** — the full suite passes anywhere in seconds, no Docker daemon required.

---

## Full Docker setup (from repo root)

See the root `README.md` for the complete Docker Compose workflow and make targets.
