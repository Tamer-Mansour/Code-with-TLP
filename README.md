# 📚 Studying App

> A LeetCode-style platform for studying computer science and programming.
> Browse subjects, follow courses, complete lessons, and solve code exercises
> with a real in-browser editor — graded by a sandboxed multi-language judge.

<p align="left">
  <img alt="Python"   src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI"  src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white">
  <img alt="SQLite"   src="https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white">
  <img alt="Docker"   src="https://img.shields.io/badge/Docker-sandbox-2496ED?logo=docker&logoColor=white">
  <img alt="Angular"  src="https://img.shields.io/badge/Angular-planned-DD0031?logo=angular&logoColor=white">
  <img alt="Monaco"   src="https://img.shields.io/badge/Monaco_Editor-planned-0078D4?logo=visualstudiocode&logoColor=white">
  <img alt="Tests"    src="https://img.shields.io/badge/Tests-pytest_~69-0A9EDC?logo=pytest&logoColor=white">
  <img alt="Status"   src="https://img.shields.io/badge/Status-backend_ready-success">
</p>

---

## ✨ Features

- 🧱 **Hierarchical catalog** — Subjects → Courses → Modules → Lessons → Exercises
- 🔐 **JWT auth** — access + refresh tokens, bcrypt hashing, role-based admin
- 🧪 **LeetCode-style judge** — runs Python, JavaScript, TypeScript, Java, and C# in throwaway Docker containers (no network, capped CPU/RAM/PIDs)
- ✅ **Scoring** — weighted test cases, visible + hidden, whitespace-tolerant comparison
- 📈 **Progress tracking** — enrollments, lesson progress, auto-recomputed course percentages
- 🛠 **Admin panel API** — full CRUD over the catalog + users + submissions browser + stats
- 📜 **Swagger UI** — paste your JWT into the Authorize button and try every endpoint
- 🧰 **~69 pytest tests** — Docker is mocked so the suite runs anywhere

---

## 🗂 Project structure

```
stdying-app/
├── backend/                   # FastAPI service (this repo currently)
│   ├── app/                   # Source
│   ├── docker/runners/        # Per-language sandbox Dockerfiles
│   ├── tests/                 # Pytest suite (git-ignored)
│   ├── requirements.txt
│   └── README.md              # Backend-specific docs
├── frontend/                  # Angular app (coming next)
├── plan.md                    # Detailed roadmap (done + next)
└── README.md                  # ← you are here
```

---

## 🚀 Quick start (backend)

> Requires **Python 3.11+** and (for code execution) **Docker Desktop** running.

```powershell
cd backend

# 1) virtual env + dependencies
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2) configure
copy .env.example .env       # then edit SECRET_KEY and FIRST_ADMIN_PASSWORD

# 3) build language sandboxes
.\docker\runners\build-all.ps1

# 4) seed the database
python -m app.seed

# 5) run the API
uvicorn app.main:app --reload --port 8000
```

Then open **http://localhost:8000/docs** and you're in business.

---

## 🔑 How to authenticate in Swagger

1. Expand **POST `/api/v1/auth/login`**, click **Try it out**, send `{ "identifier": "<email_or_username>", "password": "..." }`.
2. Copy the `access_token` from the response.
3. Click the green **🔒 Authorize** button at the top.
4. Paste the token (just the token — no `Bearer ` prefix). Click **Authorize**, then **Close**.
5. Every subsequent request uses your token automatically (it persists across reloads).

> Tip: for admin-only endpoints under `/api/v1/admin/...`, log in as the seeded admin user — credentials come from your `.env` file.

---

## 🧠 How the judge works

```
Client                FastAPI              code_runner               Docker
  │                     │                      │                      │
  ├── POST /submissions ├──► grade_submission ─┤                      │
  │                     │                      │── create container ──►
  │                     │                      │  (--network none,    │
  │                     │                      │   mem=256m, cpu=0.5, │
  │                     │                      │   pids=128, ro-fs)   │
  │                     │                      │◄── stdout/stderr ────│
  │                     │                      │                      │
  │                     │   for every test case (visible + hidden)    │
  │                     │                                             │
  │◄── status, score, per-test results ─────────                      │
```

| Outcome | Status |
| --- | --- |
| All test cases pass | `accepted` |
| Output differs | `wrong_answer` |
| Wall-clock exceeded | `time_limit_exceeded` |
| OOM-killed by Docker | `memory_limit_exceeded` |
| Non-zero exit code | `runtime_error` |
| Compile failure | `compile_error` |
| Runner / Docker error | `internal_error` |

---

## 🧪 Running the tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -v
# or with coverage:
pytest --cov=app --cov-report=term-missing
```

Docker is **mocked** in tests — the suite runs in a couple of seconds with no Docker required.

> Test files live under `backend/tests/` but are intentionally **git-ignored** so they stay out of version control.

---

## 🌐 API surface (under `/api/v1`)

| Group | Sample endpoints |
| --- | --- |
| **Auth** | `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me` |
| **Users** | `GET /users/me`, `PATCH /users/me` |
| **Catalog** | `GET /catalog/subjects`, `GET /catalog/courses?q=`, `GET /catalog/courses/{slug}`, `GET /catalog/exercises/{slug}` |
| **Submissions** | `POST /submissions/run` (ad-hoc), `POST /submissions` (graded), `GET /submissions/me` |
| **Progress** | `POST /progress/enroll/{course_id}`, `PUT /progress/lessons/{id}` |
| **Admin** | `GET /admin/stats`, full CRUD over users, courses, modules, lessons, exercises, test-cases, submission browser |

See [`backend/README.md`](backend/README.md) for the complete list and [`plan.md`](plan.md) for the full roadmap.

---

## 🛣 Roadmap

- ✅ Backend, code judge, admin API, tests, Swagger
- ⏳ **Angular frontend** — auth flow, catalog browsing, Monaco-powered exercise page, student dashboard, admin panel
- ⏳ Production hardening — Alembic migrations, Postgres swap, background job queue for grading, rate-limiting

The full plan (including the test plan) lives in [`plan.md`](plan.md).

---

## ⚙️ Tech stack

**Backend** · FastAPI · Uvicorn · SQLAlchemy 2.0 · Pydantic v2 · python-jose · passlib (bcrypt) · docker-py
**Database** · SQLite (default) — switch to PostgreSQL by changing `DATABASE_URL`
**Sandboxing** · Docker — one container per test case, hard CPU / RAM / PID / network caps
**Testing** · pytest · httpx · pytest-cov · ~69 tests, Docker mocked

---

## 📄 License

Personal study project. Adapt freely.
