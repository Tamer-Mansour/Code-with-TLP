# Studying App — top-level Makefile
# Works on Windows (with GNU make from Chocolatey) and Unix-like systems.
# Run `make help` to see all targets.

# ---------- OS detection ----------
ifeq ($(OS),Windows_NT)
	PYTHON     := python
	VENV_BIN   := backend/.venv/Scripts
	PY         := $(VENV_BIN)/python.exe
	PIP        := $(VENV_BIN)/python.exe -m pip
	UVICORN    := $(VENV_BIN)/uvicorn.exe
	PYTEST     := $(VENV_BIN)/python.exe -m pytest
	BUILD_RUNNERS := powershell -ExecutionPolicy Bypass -File backend/docker/runners/build-all.ps1
	RMRF       := powershell -Command "Remove-Item -Recurse -Force"
	NULL       := nul
else
	PYTHON     := python3
	VENV_BIN   := backend/.venv/bin
	PY         := $(VENV_BIN)/python
	PIP        := $(VENV_BIN)/pip
	UVICORN    := $(VENV_BIN)/uvicorn
	PYTEST     := $(VENV_BIN)/pytest
	BUILD_RUNNERS := bash backend/docker/runners/build-all.sh
	RMRF       := rm -rf
	NULL       := /dev/null
endif

PORT ?= 8000
HOST ?= 0.0.0.0

.DEFAULT_GOAL := help

# ---------- Help ----------
.PHONY: help
help: ## Show this help
	@echo Code with TLP — Makefile targets:
	@echo.
	@echo   Backend:
	@echo   make install              Create venv and install backend dependencies
	@echo   make env                  Copy backend/.env.example to backend/.env (if missing)
	@echo   make runners              Build the Docker sandbox images (Python/Node/Java/C#)
	@echo   make seed                 Run the database seed (admin + sample course/exercise)
	@echo   make run                  Start the FastAPI server on $(HOST):$(PORT) with reload
	@echo   make test                 Run the pytest suite
	@echo   make test-cov             Run pytest with coverage report
	@echo   make health               Curl /health and print the response
	@echo   make swagger              Open Swagger UI in the default browser
	@echo   make bootstrap            install + env + seed (one-shot setup, no Docker required)
	@echo.
	@echo   Frontend:
	@echo   make frontend-install     Install Angular frontend dependencies
	@echo   make frontend-dev         Start Angular dev server on :4200
	@echo   make frontend-build       Build Angular app for production
	@echo.
	@echo   Docker (full stack):
	@echo   make docker-up              Build images and start all containers (first run)
	@echo   make docker-start           Start containers without rebuilding
	@echo   make docker-down            Stop and remove all containers
	@echo   make docker-restart         Restart all containers (no rebuild)
	@echo   make docker-update-backend  Rebuild backend image and restart it
	@echo   make docker-update-frontend Rebuild frontend image and restart it
	@echo   make docker-ps              Show container status
	@echo   make docker-logs            Tail all container logs
	@echo   make docker-logs-backend    Tail backend logs only
	@echo   make docker-logs-frontend   Tail frontend logs only
	@echo   make docker-seed            Run seed inside the running backend container
	@echo.
	@echo   Misc:
	@echo   make clean                Remove venv, caches, and the SQLite database
	@echo   make freeze               Show installed package versions
	@echo   make git-status           Show repo status

# ---------- Setup ----------
.PHONY: install
install: ## Create venv and install backend dependencies
	@echo === Creating virtualenv ===
	@$(PYTHON) -m venv backend/.venv
	@echo === Upgrading pip ===
	@$(PIP) install --upgrade pip
	@echo === Installing requirements ===
	@$(PIP) install -r backend/requirements.txt
	@echo === Install complete ===

.PHONY: env
env: ## Copy backend/.env.example to backend/.env if missing
ifeq ($(OS),Windows_NT)
	@if not exist backend\.env (copy backend\.env.example backend\.env >$(NULL) && echo Created backend\.env) else echo backend\.env already exists
else
	@[ -f backend/.env ] || (cp backend/.env.example backend/.env && echo "Created backend/.env")
endif

.PHONY: runners
runners: ## Build the Docker runner images
	@$(BUILD_RUNNERS)

# ---------- Run / seed ----------
# Use $(abspath ...) so these work from any shell on Windows and Unix.
ABS_PY     := $(abspath $(PY))
ABS_UVICORN:= $(abspath $(UVICORN))
ABS_PYTEST := $(abspath $(firstword $(PYTEST)))

.PHONY: seed
seed: ## Populate the DB with admin + sample course/exercise
	cd backend && "$(ABS_PY)" -m app.seed

.PHONY: run
run: ## Start the FastAPI server with --reload
	cd backend && "$(ABS_UVICORN)" app.main:app --reload --host $(HOST) --port $(PORT)

.PHONY: run-prod
run-prod: ## Start the FastAPI server without reload (single worker)
	cd backend && "$(ABS_UVICORN)" app.main:app --host $(HOST) --port $(PORT) --workers 1

# ---------- Tests ----------
.PHONY: test
test: ## Run the pytest suite
	cd backend && "$(ABS_PY)" -m pytest -v

.PHONY: test-cov
test-cov: ## Run pytest with coverage
	cd backend && "$(ABS_PY)" -m pytest --cov=app --cov-report=term-missing --cov-report=html

# ---------- Utilities ----------
.PHONY: health
health: ## Curl /health and print the response
	curl -s http://localhost:$(PORT)/health

.PHONY: swagger
swagger: ## Open Swagger UI in the default browser
ifeq ($(OS),Windows_NT)
	@start http://localhost:$(PORT)/docs
else
	@xdg-open http://localhost:$(PORT)/docs 2>/dev/null || open http://localhost:$(PORT)/docs
endif

.PHONY: freeze
freeze: ## Show installed package versions
	@$(PIP) freeze

.PHONY: git-status
git-status: ## git status
	@git status

# ---------- Frontend ----------
.PHONY: frontend-install
frontend-install: ## Install Angular frontend dependencies
	cd frontend && npm install

.PHONY: frontend-dev
frontend-dev: ## Start Angular dev server on :4200
	cd frontend && npm start

.PHONY: frontend-build
frontend-build: ## Build Angular app for production
	cd frontend && npm run build

# ---------- Docker (full stack) ----------
.PHONY: docker-up
docker-up: ## Build images and start all containers (use for first run or after dep changes)
	docker compose up --build -d

.PHONY: docker-start
docker-start: ## Start containers without rebuilding
	docker compose up -d

.PHONY: docker-down
docker-down: ## Stop and remove all containers
	docker compose down

.PHONY: docker-restart
docker-restart: ## Restart all containers without rebuilding
	docker compose restart

.PHONY: docker-update-backend
docker-update-backend: ## Rebuild only the backend image and restart it
	docker compose build backend
	docker compose up -d --no-deps backend

.PHONY: docker-update-frontend
docker-update-frontend: ## Rebuild only the frontend image and restart it
	docker compose build frontend
	docker compose up -d --no-deps frontend

.PHONY: docker-ps
docker-ps: ## Show running container status
	docker compose ps

.PHONY: docker-logs
docker-logs: ## Tail all container logs
	docker compose logs -f

.PHONY: docker-logs-backend
docker-logs-backend: ## Tail backend container logs
	docker compose logs -f backend

.PHONY: docker-logs-frontend
docker-logs-frontend: ## Tail frontend container logs
	docker compose logs -f frontend

.PHONY: docker-seed
docker-seed: ## Run seed inside the running backend container
	docker compose exec backend python -m app.seed

# ---------- Composed targets ----------
.PHONY: bootstrap
bootstrap: install env seed ## install + env + seed (no Docker needed)
	@echo === Bootstrap complete ===
	@echo Run "make test" to verify, "make run" to start the API.

.PHONY: all
all: bootstrap runners ## Full setup including Docker sandbox images
	@echo === Full setup complete ===
	@echo Run "make run" to start the API.

# ---------- Cleanup ----------
.PHONY: clean
clean: ## Remove venv, caches, and the SQLite database
ifeq ($(OS),Windows_NT)
	-@if exist backend\.venv $(RMRF) backend\.venv
	-@if exist backend\.pytest_cache $(RMRF) backend\.pytest_cache
	-@if exist backend\htmlcov $(RMRF) backend\htmlcov
	-@if exist backend\studying_app.db del backend\studying_app.db
else
	-$(RMRF) backend/.venv backend/.pytest_cache backend/htmlcov backend/studying_app.db
endif
	@echo === Clean complete ===
