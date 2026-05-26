# Semantic Versioning

Every software project that is consumed by others — a library, an API, a CLI tool — needs a version number. Semantic Versioning (SemVer) is the most widely adopted standard for making version numbers communicate meaning rather than just sequence.

## The SemVer Specification

A SemVer version has the form `MAJOR.MINOR.PATCH`, for example `2.14.3`:

| Field | Increment when | Example trigger |
|---|---|---|
| `MAJOR` | Backward-incompatible ("breaking") changes | Removing a function from a public API |
| `MINOR` | New functionality, backward-compatible | Adding a new optional parameter |
| `PATCH` | Backward-compatible bug fixes | Fixing an off-by-one error |

When you increment `MAJOR`, reset `MINOR` and `PATCH` to 0. When you increment `MINOR`, reset `PATCH` to 0.

```
1.4.2  →  1.4.3   (patch: bug fix)
1.4.3  →  1.5.0   (minor: new feature)
1.5.0  →  2.0.0   (major: breaking API change)
2.0.0  →  2.0.1   (patch: hot fix on the new major)
```

## Version 0.x: Initial Development

When `MAJOR` is 0 (e.g., `0.4.2`), the API is considered unstable. Anything may change at any time. The public API should not be considered stable until version `1.0.0`.

Many open source projects stay at `0.x` for years. Once they declare `1.0.0`, they commit to the SemVer contract.

## Pre-Release and Build Metadata

```
1.0.0-alpha          # alpha release (first testing)
1.0.0-alpha.1        # second alpha
1.0.0-beta.3         # third beta
1.0.0-rc.1           # release candidate 1
1.0.0                # stable release

1.0.0+20240301.sha.a1b2c3   # build metadata (ignored in comparisons)
```

Pre-release versions have lower precedence than the associated normal version: `1.0.0-alpha < 1.0.0`.

## Why SemVer Matters for Dependency Management

Package managers (pip, npm, cargo, maven) use SemVer to resolve compatible dependency versions:

```toml
# pyproject.toml (Python)
requests = ">=2.28.0,<3.0.0"   # any 2.x from 2.28 onwards
```

```json
// package.json (Node.js)
"express": "^4.18.2"   // ^: compatible with 4.18.2, meaning >=4.18.2 <5.0.0
"lodash": "~4.17.21"   // ~: patch-level updates only, meaning >=4.17.21 <4.18.0
```

If every library author respected SemVer strictly, dependency hell would be rare. In practice:
- Many projects accidentally introduce breaking changes in patch releases
- Some projects use MAJOR bumps as marketing (React 18, Angular 15) rather than pure API-breakage signals
- `0.x` projects make no compatibility guarantees

This is why pinning exact versions in production (`requests==2.31.0`) is common for deployment artifacts, while using ranges is common in library specifications.

## SemVer in Practice: A Library Maintainer's Checklist

Before releasing, classify your changes:

**Breaking changes (MAJOR bump):**
- Removing a public function, class, or method
- Changing a function's signature in an incompatible way (removing a required parameter, changing a return type)
- Changing a config file format in an incompatible way
- Removing support for a runtime version (e.g., dropping Python 3.8)

**New features (MINOR bump):**
- Adding a new optional parameter (with a default value)
- Adding a new public function or class
- Adding a new configuration option that does not affect existing configurations
- Marking something as deprecated (removal will come in a future MAJOR)

**Bug fixes (PATCH bump):**
- Correcting incorrect behavior without changing the public interface
- Fixing documentation
- Improving performance without changing results
- Fixing security vulnerabilities that don't require API changes

## Conventional Commits and Automated Versioning

**Conventional Commits** is a specification for commit messages that encodes the type of change:

```
feat: add batch export endpoint
^     ^
│     └── description
└── type (feat | fix | docs | style | refactor | test | chore)

fix!: remove deprecated v1 auth header support
   ^
   └── "!" marks a BREAKING CHANGE → triggers MAJOR bump
```

With conventional commits, tools like `semantic-release` or `release-please` can:
1. Read the commit log since the last release
2. Determine the appropriate version bump automatically
3. Generate a `CHANGELOG.md` from commit messages
4. Create a Git tag and GitHub release

Example of a `CHANGELOG.md` entry generated from conventional commits:

```markdown
## [2.1.0] - 2024-03-15

### Features
- add batch export endpoint (#234)
- support webhook retry configuration (#229)

### Bug Fixes
- handle empty list in aggregation (#241)
- round currency to 2 decimal places (#238)
```

## SemVer Comparison Algorithm

Comparing `2.10.0` vs `2.9.9` correctly requires numeric comparison, not lexicographic:

```python
# Lexicographic (WRONG):
"2.10.0" < "2.9.9"   # True — "1" < "9" in string comparison

# Numeric (CORRECT):
(2, 10, 0) > (2, 9, 9)   # True — 10 > 9
```

This is a classic gotcha when sorting version strings. Always split on `.` and compare each component as an integer.

## Lock Files and Reproducible Builds

For applications (as opposed to libraries), pin all dependency versions in a lock file:

```
# pip: requirements.txt (or pip.lock in newer tooling)
requests==2.31.0
urllib3==2.0.7
certifi==2024.2.2

# npm: package-lock.json (auto-generated)
# Python poetry: poetry.lock
# Rust cargo: Cargo.lock
```

Lock files ensure that every developer, every CI run, and every production deployment installs the exact same dependency tree. Without them, a patch release to a transitive dependency could silently change behavior in production.

The recommended practice:
- **Libraries:** commit `pyproject.toml` / `package.json` with version ranges; do NOT commit lock files (consumers resolve their own versions)
- **Applications:** commit lock files to ensure reproducibility

## Summary

- `MAJOR.MINOR.PATCH` communicates the type of change to consumers
- `0.x` means unstable API; `1.0.0` commits to the SemVer contract
- Pre-release tags (`-alpha`, `-rc.1`) convey readiness level
- Package manager range specifiers (`^`, `~`, `>=`) use SemVer to resolve compatible versions
- Conventional commits enable automated version bumping and changelog generation
- Always compare SemVer components numerically, not lexicographically
