# Video: CI/CD Pipeline Full Tutorial

This video walks through building a complete CI/CD pipeline from zero using GitHub Actions, Docker, and a cloud hosting platform. The instructor commits code, watches the pipeline run, sees a test failure block the merge, fixes the test, and watches the fixed build deploy automatically to a staging environment.

**Key takeaways:**
- Anatomy of a GitHub Actions workflow: triggers, jobs, steps, runners, and how to use marketplace actions for common tasks (checkout, setup language, upload artifacts).
- Building a CI stage: running linters, type checkers, unit tests with coverage thresholds, and integration tests with a real database service container.
- Containerizing an application with a multi-stage Dockerfile to keep the production image lean and secure.
- CD stage: pushing a Docker image to a registry, deploying to a staging environment automatically, and gating the production deploy behind a manual approval.
- Deployment strategies compared in a live demo: rolling update versus blue/green cutover, with a demonstration of instant rollback.
