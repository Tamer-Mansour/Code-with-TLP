# venv, pip, and Packaging

## Virtual environments

A venv is an isolated Python install: its own interpreter, its own packages, no contamination with system Python or other projects.

```bash
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
.venv\Scripts\activate             # Windows
deactivate                          # leave
```

Once activated, `python` and `pip` point inside `.venv`. Per-project venvs are the universal convention.

## Installing packages

```bash
pip install requests
pip install "django>=5,<6"
pip install -r requirements.txt
pip install -e .                   # install the current project, editable
pip uninstall requests
pip list
pip show requests
pip freeze > requirements.txt
```

## A modern alternative: uv

`uv` is a fast, all-in-one replacement for `pip` and `venv`:

```bash
uv venv
uv pip install requests
uv pip sync requirements.txt
```

10–100x faster, single binary, no Python boostrap needed. Worth adopting on new projects.

## pyproject.toml — the modern manifest

```toml
[project]
name = "myproject"
version = "0.1.0"
description = "..."
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.110",
  "httpx>=0.27",
]

[project.optional-dependencies]
dev = ["pytest", "ruff", "mypy"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

This is the file *all* modern Python projects should have. `setup.py` is legacy.

## Build and publish

```bash
pip install build twine
python -m build                    # produces wheel + sdist in dist/
twine upload dist/*                # to PyPI (after account + token setup)
```

Or skip both — use Hatch or PDM, which bundle build + publish.

## Application vs library distribution

- A **library** you install with `pip install`. Pin loose ranges.
- An **application** you ship with **pinned** dependencies for reproducibility. Use a lockfile (`uv lock`, `pip-compile`, Poetry).

## Tools you'll actually use

| Tool        | What it does                                     |
|-------------|--------------------------------------------------|
| `uv`        | Fast venv + dependency manager.                  |
| `ruff`      | Linter + formatter (replaces flake8 + black).    |
| `mypy`/`pyright` | Static type checker.                        |
| `pytest`    | The standard test runner.                        |
| `pre-commit`| Run linters/formatters on `git commit`.          |
| `tox`/`nox` | Run tests across Python versions.                |

## Multiple Python versions

Use `pyenv` (or `uv`) to manage interpreter installs:

```bash
pyenv install 3.12.3
pyenv local 3.12.3
```

Now the project's `.python-version` file pins the version everyone uses.

## A new-project quickstart

```bash
mkdir myproj && cd myproj
uv init                            # pyproject.toml + .python-version + src/myproj/
uv add fastapi httpx
uv add --dev pytest ruff mypy
uv run pytest
```

In 30 seconds you have a typed, tested, linted, reproducible Python project.
