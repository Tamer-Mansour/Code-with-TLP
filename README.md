# Code with TLP

> A LeetCode-style full-stack platform for studying computer science and programming.
> Browse subjects, follow courses, complete lessons, and solve coding exercises
> with a real in-browser editor — graded by a sandboxed multi-language judge.

<p align="left">
  <img alt="Python"    src="https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI"   src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white">
  <img alt="Angular"   src="https://img.shields.io/badge/Angular-21-DD0031?logo=angular&logoColor=white">
  <img alt="SQLite"    src="https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white">
  <img alt="Docker"    src="https://img.shields.io/badge/Docker-sandbox-2496ED?logo=docker&logoColor=white">
  <img alt="Tests"     src="https://img.shields.io/badge/Tests-pytest_~69-0A9EDC?logo=pytest&logoColor=white">
  <img alt="Status"    src="https://img.shields.io/badge/Status-full--stack_ready-success">
</p>

---

## Features

- **Hierarchical catalog** — Subjects → Courses → Modules → Lessons → Exercises
- **JWT authentication** — access tokens (60 min) + refresh tokens (14 days), bcrypt hashing, role-based access (student / admin)
- **LeetCode-style judge** — runs Python, JavaScript, TypeScript, Java, and C# in throwaway Docker containers (no network, capped CPU / RAM / PIDs)
- **Scoring** — weighted test cases, visible + hidden, whitespace-tolerant comparison
- **Progress tracking** — enrollments, lesson progress, auto-recomputed course completion percentages
- **Ranked profile** — Steam-style profile page with 8 tiers (Newcomer → Legend) based on total score; animated banner, avatar glow, and progress bar that evolve with rank; customizable banner style (gradient / geometric / mesh)
- **Admin panel** — full CRUD over catalog, users, submissions browser, and live stats dashboard
- **Monaco editor** — JetBrains Darcula theme, bracket-pair colorization, smooth caret animation, language-aware syntax highlighting; loaded from CDN
- **Dark / light mode** — persisted in `localStorage`, defaults to light
- **Swagger UI** — paste your JWT into the Authorize dialog and explore every endpoint at `/docs`
- **~69 pytest tests** — Docker is mocked so the full suite runs anywhere without Docker

---

## Project structure

```
code-with-tlp/
├── backend/                   # FastAPI service
│   ├── app/
│   │   ├── main.py            # App factory, CORS, global exception handler
│   │   ├── seed.py            # Seed admin + sample course/exercise
│   │   ├── core/              # config, database, security
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── api/
│   │   │   ├── deps.py        # Auth dependencies
│   │   │   └── routes/        # auth, users, catalog, submissions, progress, admin
│   │   └── services/
│   │       ├── code_runner.py # Docker-backed sandbox runner
│   │       └── judge.py       # Score a submission against test cases
│   ├── docker/runners/        # Per-language sandbox Dockerfiles
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                  # Angular 21 app
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/          # Services, guards, interceptors, models
│   │   │   ├── shared/        # Navbar, ToastContainer, MonacoEditor
│   │   │   └── features/      # auth, catalog, exercises, dashboard, admin, profile
│   │   ├── styles.scss        # Tailwind + CSS variable theme tokens + rank animations
│   │   └── index.html
│   ├── Dockerfile             # Multi-stage: Node 22 build → nginx serve
│   ├── nginx.conf             # SPA routing + /api/ proxy to backend
│   └── tailwind.config.js
├── docker-compose.yml         # Backend + frontend services
├── Makefile                   # GNU make targets (works on Windows + Unix)
├── make.ps1                   # PowerShell wrapper (no make required)
└── README.md
```

---

## Quick start

### Option A — Docker only (recommended)

**Prerequisites:** Docker Desktop

```powershell
cp backend/.env.example backend/.env   # set SECRET_KEY and FIRST_ADMIN_PASSWORD
make docker-up                         # build images and start both containers
make docker-seed                       # seed admin user + sample data
```

- **App:** http://localhost:4200
- **API / Swagger:** http://localhost:8000/docs

After that, you only need to rebuild when code changes:

```powershell
make docker-update-frontend   # after Angular code changes
make docker-update-backend    # after requirements.txt changes
# backend .py changes auto-reload via uvicorn --reload + volume mount
```

---

### Option B — Local dev (Docker only for sandbox runners)

**Prerequisites:** Python 3.13+, Node 22+, Docker Desktop

```powershell
# Backend
make bootstrap        # create venv + .env + seed the database
make runners          # build sandbox images (requires Docker Desktop)
make run              # start FastAPI on :8000 with hot reload

# Frontend (separate terminal)
make frontend-install # npm install
make frontend-dev     # Angular dev server on :4200
```

No `make`? Use the PowerShell wrapper with the same target names:

```powershell
.\make.ps1 bootstrap
.\make.ps1 run
.\make.ps1 frontend-dev
```

---

## Make targets

### Backend

| Target | Description |
|--------|-------------|
| `install` | Create venv and install Python dependencies |
| `env` | Copy `backend/.env.example` → `backend/.env` if missing |
| `runners` | Build per-language Docker sandbox images |
| `seed` | Seed admin user + sample course and exercise |
| `run` | Start FastAPI with uvicorn hot-reload on `:8000` |
| `run-prod` | Start FastAPI without reload (single worker) |
| `test` | Run the full pytest suite |
| `test-cov` | Run pytest with coverage report |
| `bootstrap` | `install` + `env` + `seed` in one step |
| `health` | Hit `/health` and print the response |
| `swagger` | Open Swagger UI in the default browser |

### Frontend

| Target | Description |
|--------|-------------|
| `frontend-install` | `npm install` |
| `frontend-dev` | Angular dev server on `:4200` |
| `frontend-build` | Production build |

### Docker

| Target | Description |
|--------|-------------|
| `docker-up` | Build images and start all containers (first run / dep changes) |
| `docker-start` | Start containers without rebuilding |
| `docker-down` | Stop and remove all containers |
| `docker-restart` | Restart all containers without rebuilding |
| `docker-update-backend` | Rebuild backend image and restart it |
| `docker-update-frontend` | Rebuild frontend image and restart it |
| `docker-ps` | Show running container status |
| `docker-logs` | Tail logs for all services |
| `docker-logs-backend` | Tail backend container logs |
| `docker-logs-frontend` | Tail frontend container logs |
| `docker-seed` | Run seed inside the running backend container |

---

## Authenticating in Swagger

1. Open **http://localhost:8000/docs**
2. Expand **POST `/api/v1/auth/login`**, click **Try it out**, and send:
   ```json
   { "identifier": "admin@studying.app", "password": "<FIRST_ADMIN_PASSWORD from .env>" }
   ```
3. Copy the `access_token` from the response.
4. Click **Authorize** at the top of the page.
5. Paste the token (no `Bearer ` prefix). Click **Authorize**, then **Close**.

All subsequent requests in the session will include your token automatically.

---

## How the judge works

```
Client                FastAPI              code_runner               Docker
  │                     │                      │                      │
  ├── POST /submissions ├──► grade_submission ─┤                      │
  │                     │                      ├── create container ──►
  │                     │                      │  (--network none,    │
  │                     │                      │   mem=256m, cpu=0.5, │
  │                     │                      │   pids=128)          │
  │                     │                      │◄── stdout/stderr ────┤
  │                     │                      │                      │
  │                     │     repeated per test case (visible + hidden)│
  │◄── status, score, per-test results ─────────                      │
```

| Outcome | Status |
|---------|--------|
| All test cases pass | `accepted` |
| Output differs from expected | `wrong_answer` |
| Wall-clock timeout exceeded | `time_limit_exceeded` |
| OOM-killed by Docker | `memory_limit_exceeded` |
| Non-zero exit code | `runtime_error` |
| Compilation failure | `compile_error` |
| Runner / Docker error | `internal_error` |

---

## Rank system

The profile page shows a Steam-style rank that evolves automatically with your total score (sum of accepted submission scores):

| Tier | Name | Min score | Visual |
|------|------|-----------|--------|
| 0 | Newcomer | 0 | Gray banner |
| 1 | Bronze | 10 | Warm brown |
| 2 | Silver | 50 | Steel blue |
| 3 | Gold | 150 | Rich gold |
| 4 | Platinum | 400 | Cyan / teal |
| 5 | Diamond | 900 | Indigo + shimmer + glow ring |
| 6 | Master | 2 000 | Purple + shimmer + glow ring |
| 7 | Legend | 5 000 | Crimson + shimmer + glow ring |

Profile banner style (gradient / geometric / mesh) and avatar URL are customizable and persisted in `localStorage`.

---

## Running the tests

```powershell
make test       # run the ~69-test pytest suite
make test-cov   # run with coverage report
```

Docker is **mocked** in tests — the suite completes in seconds with no Docker required.

---

## API surface (under `/api/v1`)

| Group | Sample endpoints |
|-------|-----------------|
| **Auth** | `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `GET /auth/me` |
| **Users** | `GET /users/me`, `PATCH /users/me` |
| **Catalog** | `GET /catalog/subjects`, `GET /catalog/courses?q=`, `GET /catalog/courses/{slug}`, `GET /catalog/exercises/{slug}` |
| **Submissions** | `POST /submissions/run` (ad-hoc), `POST /submissions` (graded), `GET /submissions/me` |
| **Progress** | `POST /progress/enroll/{course_id}`, `PUT /progress/lessons/{id}` |
| **Admin** | `GET /admin/stats`, full CRUD over users, courses, modules, lessons, exercises, test cases, submission browser |

Full endpoint list and interactive docs: **http://localhost:8000/docs**

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| **Backend** | FastAPI 0.115, SQLAlchemy 2.0, Pydantic v2, python-jose, passlib (bcrypt), docker-py |
| **Database** | SQLite (default) — swap to PostgreSQL by changing `DATABASE_URL` |
| **Sandboxing** | Docker — one container per test case, hard CPU / RAM / PID / network caps |
| **Frontend** | Angular 21, Tailwind CSS v3, Monaco Editor with Darcula theme (CDN), ngx-markdown, lucide-angular |
| **Testing** | pytest ~69 tests (Docker mocked) |
| **Infrastructure** | Docker Compose, GNU Make + PowerShell wrapper, nginx (SPA + reverse proxy) |

---

## Roadmap

- [x] Backend — FastAPI, judge, admin API, Swagger, ~69 pytest tests
- [x] Frontend — Angular 21, all pages, Monaco Darcula editor, dark/light mode
- [x] Docker Compose — backend + frontend fully containerized, hot-reload in dev
- [x] Profile — Steam-style ranked profile, 8 tiers, animated banner/glow, customization
- [ ] Alembic migrations + PostgreSQL support
- [ ] Background job queue for async grading
- [ ] Rate limiting

---

## License

Personal study project. Adapt freely.
