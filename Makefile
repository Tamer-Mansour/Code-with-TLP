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
	@echo Studying App targets:
	@echo.
	@echo   make install         Create venv and install backend dependencies
	@echo   make env             Copy backend/.env.example to backend/.env (if missing)
	@echo   make runners         Build the Docker sandbox images (Python/Node/Java/C#)
	@echo   make seed            Run the database seed (admin + sample course/exercise)
	@echo   make run             Start the FastAPI server on $(HOST):$(PORT) with reload
	@echo   make test            Run the pytest suite
	@echo   make test-cov        Run pytest with coverage report
	@echo   make health          Curl /health and print the response
	@echo   make swagger         Open Swagger UI in the default browser
	@echo   make bootstrap       install + env + seed (one-shot setup, no Docker required)
	@echo   make all             bootstrap + runners (full setup, Docker required)
	@echo   make clean           Remove venv, caches, and the SQLite database file
	@echo   make freeze          Show installed package versions
	@echo   make git-status      Show repo status

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
.PHONY: seed
seed: ## Populate the DB with admin + sample course/exercise
	cd backend && ../$(PY) -m app.seed

.PHONY: run
run: ## Start the FastAPI server with --reload
	cd backend && ../$(UVICORN) app.main:app --reload --host $(HOST) --port $(PORT)

.PHONY: run-prod
run-prod: ## Start the FastAPI server without reload (single worker)
	cd backend && ../$(UVICORN) app.main:app --host $(HOST) --port $(PORT) --workers 1

# ---------- Tests ----------
.PHONY: test
test: ## Run the pytest suite
	cd backend && ../$(PYTEST) -v

.PHONY: test-cov
test-cov: ## Run pytest with coverage
	cd backend && ../$(PYTEST) --cov=app --cov-report=term-missing --cov-report=html

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
