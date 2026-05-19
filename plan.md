# Studying App — Project Plan

A LeetCode-style full-stack studying platform for computer-science subjects.
**Backend:** FastAPI + SQLite + Docker code sandbox.
**Frontend (planned):** Angular (standalone APIs) + Monaco editor.

---

## 1. Status snapshot

| Area | Status |
| --- | --- |
| Backend scaffold | ✅ Done |
| Database models | ✅ Done |
| Auth (JWT access + refresh) | ✅ Done |
| Public catalog API | ✅ Done |
| Student progress API | ✅ Done |
| Docker code runner | ✅ Done |
| Judge / grading | ✅ Done |
| Admin panel API | ✅ Done |
| Seed data | ✅ Done |
| Swagger w/ bearer paste | ✅ Done |
| Test suite (pytest, ~69 tests) | ✅ Done |
| Frontend (Angular) | ⏳ Next |
| Production hardening | ⏳ Later |

---

## 2. What was built

### 2.1 Backend layout

```
backend/
├── app/
│   ├── main.py                # FastAPI app, CORS, Swagger w/ BearerAuth
│   ├── seed.py                # Seed admin + sample course/exercise
│   ├── core/                  # config, db, security (bcrypt + JWT)
│   ├── models/                # SQLAlchemy 2.0 models
│   ├── schemas/               # Pydantic v2 request/response schemas
│   ├── api/
│   │   ├── deps.py            # get_current_user / get_current_admin
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── catalog.py     # public reads
│   │       ├── submissions.py # Run + Submit (graded)
│   │       ├── progress.py    # enroll, lesson progress
│   │       └── admin.py       # role=admin CRUD over everything
│   └── services/
│       ├── code_runner.py     # Docker sandbox
│       └── judge.py           # Run all test cases, score, persist
├── docker/runners/            # Dockerfiles per language + build scripts
├── tests/                     # 69 pytest tests (Docker mocked away)
├── pytest.ini
├── requirements.txt
├── .env.example
└── README.md
```

### 2.2 Domain model

`User → Enrollment → Course → Module → Lesson → Exercise → TestCase`
plus `Submission → TestCaseResult`, `LessonProgress`, `Tag`, `LearningPath`.

| Entity | Notes |
| --- | --- |
| `User` | Roles: `student` / `admin`. Bcrypt hashed password. |
| `Subject` | E.g. Algorithms, Web Development, Databases. |
| `Course` | Belongs to a Subject. Has many Modules. `is_published` flag. |
| `Module` | Section of a Course. |
| `Lesson` | `reading` / `video` / `quiz` / `exercise`. Markdown content. |
| `Exercise` | Starter code + solution code per language (JSON map). Hidden + visible test cases. Time / memory limits. |
| `TestCase` | `stdin`, `expected_stdout`, `is_hidden`, `weight`. |
| `Submission` | Status enum (accepted / wrong_answer / TLE / MLE / RE / CE / internal_error). Score. |
| `Enrollment` | Auto-recomputed `progress_percent` based on completed lessons. |
| `LearningPath` | Curated sequence of courses. |

### 2.3 API surface (all under `/api/v1`)

**Auth** — `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me`
**Users** — `GET /users/me`, `PATCH /users/me`
**Catalog (public)** — list subjects, courses (with filters), nested course tree, exercise detail (hidden test cases + solution stripped), learning paths, tags
**Submissions** — `POST /submissions/run` (ad-hoc), `POST /submissions` (graded), history, single-submission read with ACL
**Progress** — enroll / unenroll, lesson progress with course % recomputation
**Admin** (`role=admin` required) — stats dashboard, full CRUD over users/courses/modules/lessons/exercises/test-cases, submission browser

### 2.4 Code execution (LeetCode-style)

- Each test case runs in a **fresh Docker container** with:
  - `--network none`
  - capped memory (default 256 MB) — `OOMKilled` ⇒ `memory_limit_exceeded`
  - capped CPU (0.5 vCPU)
  - `--pids-limit 128`, `no-new-privileges`
  - wall-clock timeout = `exercise.time_limit_ms + 1s` ⇒ `time_limit_exceeded`
- Languages: **Python, JavaScript, TypeScript, Java, C#** (`dotnet script` so a single `.csx` file runs without project boilerplate).
- Output comparison is whitespace-tolerant (trailing whitespace per line ignored).
- Hidden test cases are graded but their stdin/stdout aren't echoed back to students.
- If a runner image is missing or Docker is down, the submission returns `status=internal_error` with a clear message.

### 2.5 Swagger / OpenAPI

- `GET /docs` — Swagger UI with a green **Authorize** button.
- Paste the `access_token` from `/auth/login` (no `Bearer ` prefix needed), click Authorize, and every request uses your token.
- `persistAuthorization: true` keeps the token across page reloads.
- `GET /redoc` — alternative docs view.

### 2.6 Tests (~69)

Run from `backend/`:
```powershell
.\.venv\Scripts\pytest -v
```

| File | Covers |
| --- | --- |
| `test_security.py` | hash / verify, JWT encode / decode |
| `test_auth.py` | register, login (email + username), refresh, /me |
| `test_users.py` | self-update, password rotation |
| `test_catalog.py` | public listing, filters, exercise leak-prevention, admin gating |
| `test_submissions.py` | Run + Submit; status classification; auto-complete lesson on AC; ACL |
| `test_progress.py` | enroll idempotency, course % recomputation |
| `test_admin.py` | stats, full CRUD, role/active changes |
| `test_judge.py` | scoring logic with mocked runner; TLE/MLE/internal_error/early-exit |

Docker is **mocked** — tests pass on a machine with no Docker.

---

## 3. What's next

### 3.1 Frontend — Angular (latest, standalone APIs)

| Phase | Pages / features |
| --- | --- |
| Foundation | App shell, routing, auth interceptor (Bearer header), `AuthService` w/ refresh-token rotation, role-aware route guards |
| Student | `/login`, `/register`, `/dashboard` (enrollments + recent submissions), `/catalog`, `/subjects/:slug`, `/courses/:slug` (module/lesson tree), `/lessons/:id`, `/exercises/:slug` (Monaco split-pane editor + Run + Submit, results panel) |
| Admin | `/admin` shell w/ `roleGuard`, pages for Subjects, Courses, Modules, Lessons, Exercises (incl. test-case manager), Users, Submissions browser, Stats dashboard |
| Polish | Light/dark mode, language switcher in Monaco, syntax-highlighted markdown lesson rendering (e.g. `ngx-markdown` + `highlight.js`), submission status badges, score history chart |

### 3.2 Production hardening

- Replace `Base.metadata.create_all` with **Alembic migrations** (Alembic already in `requirements.txt`).
- Swap SQLite → **PostgreSQL** for deployment (just change `DATABASE_URL`).
- Move submission grading off the request thread (Celery or `BackgroundTasks` + queue) to avoid blocking under load.
- Per-user **submission rate-limit** at the API layer (e.g. `slowapi`).
- Pre-warm runner Docker images and cache compile output for compiled languages.
- Structured logging (`structlog`) + request-ID middleware.
- Optional: convert the runner subprocess flow to **gVisor** / **firecracker-microvm** for stronger isolation.

### 3.3 Test plan additions (after frontend lands)

- Karma/Jest **unit tests** for each Angular service (auth, catalog, submission).
- **Component tests** for `MonacoEditorComponent`, `ExerciseRunnerComponent`, `AdminTableComponent`.
- **End-to-end** with Playwright: login → enroll → solve → see score, plus admin CRUD flow.
- A **runner smoke-test script** that builds the Docker images and runs one submission per language end-to-end (kept out of the default `pytest` run because it needs Docker).

---

## 4. Run sheet

### Fast path (Makefile)

```powershell
make bootstrap   # venv + .env + seed (no Docker needed)
make runners     # build the Python/Node/Java/C# sandbox images
make test        # ~69 tests, ~15s
make run         # API on http://localhost:8000  (Swagger: /docs)
```

Run `make help` to see every target. No `make`? Use `./make.ps1 <target>` instead.

### Manual (if you prefer)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env                  # edit SECRET_KEY + FIRST_ADMIN_PASSWORD
.\docker\runners\build-all.ps1
python -m app.seed
pytest -v
uvicorn app.main:app --reload --port 8000
```

Swagger flow: http://localhost:8000/docs → login → copy `access_token` → click **Authorize** → paste → use any endpoint.

---

## 5. Decisions locked

- **DB:** SQLite for development; `DATABASE_URL` makes swap-out trivial.
- **Code execution:** Docker sandbox (chosen over Judge0 to keep the stack lean, and over local subprocess for safety).
- **Languages:** Python, JavaScript, TypeScript, Java, C#.
- **Auth:** JWT access (60 min) + refresh (14 d), bcrypt password hashing.
- **Test files are git-ignored** (per user request) — they live locally and are not committed.
