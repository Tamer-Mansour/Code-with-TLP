# Presenting Your Project

You have built a real Spring Boot + MySQL application. Now you need to show it to the world — whether that means demoing it in a job interview, posting it on GitHub for a recruiter, or walking a hiring panel through your design decisions. A project that runs but cannot be explained or found online counts for far less than one that is well-presented.

## What Reviewers Actually Look For

| Signal | What it tells them |
|--------|-------------------|
| Clean, public GitHub repository | You know professional version control habits |
| Descriptive README with setup steps | You can communicate technical context to other developers |
| Meaningful commit history | You worked iteratively, not in one giant dump |
| Passing tests or a working demo URL | The code actually runs |
| Articulate explanation of your design choices | You understand *why*, not just *how* |

## Polishing the GitHub Repository

Before sharing a link, do a final cleanup pass.

```bash
# Make sure build output is never tracked
git rm -r --cached target/
echo "target/" >> .gitignore
git add .gitignore
git commit -m "chore: ignore Maven build output"

# Check what a stranger will see when they clone your repo
git log --oneline | head -10
```

Your recent commits should tell a story — `feat: add JWT authentication`, `fix: return 404 when employee not found`, `test: add integration tests for EmployeeController` — not `asd`, `fix2`, or `final FINAL`.

### What to include in the repository

- `/src` — all source code
- `pom.xml` — dependency manifest
- `README.md` — setup and usage guide
- `schema.sql` or a Flyway/Liquibase migration folder (optional but impressive)
- `.gitignore` — targeting Java, Maven, IntelliJ, and environment files

### What to exclude

Never commit secrets or machine-specific paths. Keep a `application-local.properties` out of version control and document which variables callers must provide.

```properties
# src/main/resources/application.properties  (committed — no secrets)
spring.datasource.url=${DB_URL:jdbc:mysql://localhost:3306/employee_db}
spring.datasource.username=${DB_USER:root}
spring.datasource.password=${DB_PASSWORD}
spring.jpa.hibernate.ddl-auto=validate
```

Using environment-variable placeholders with `${VAR:default}` syntax lets the app run locally with defaults while requiring real credentials in production. This pattern shows security awareness.

## Writing a README That Works

A README is the front page of your project. Keep it short and scannable.

````markdown
# Employee Management API

A Spring Boot 3 REST API backed by MySQL 8 that manages employees and departments.

## Stack
- Java 17, Spring Boot 3.2, Spring Data JPA, Bean Validation
- MySQL 8, Flyway migrations
- Vanilla JS frontend served from `src/main/resources/static/`

## Quick Start

```bash
# 1. Create the database
mysql -u root -p -e "CREATE DATABASE employee_db;"

# 2. Configure credentials
export DB_PASSWORD=your_password

# 3. Run
./mvnw spring-boot:run
# App starts at http://localhost:8080
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/employees | List all employees |
| POST | /api/employees | Create an employee |
| PUT | /api/employees/{id} | Update an employee |
| DELETE | /api/employees/{id} | Delete an employee |

## Running Tests
```bash
./mvnw test
```
````

The key sections are: what the project does (one sentence), the technology stack, how to run it in under five commands, and the main API surface.

## Explaining Design Decisions

Interviewers will ask questions like:

- *Why did you choose Spring Data JPA instead of raw JDBC?*
- *How do you handle a request for an employee that doesn't exist?*
- *Where would you add authentication if this were a real product?*

Prepare a one-sentence answer for each major choice. For example:

> "I used `ResponseStatusException` for 404s rather than a custom exception class because the project is small and the Spring exception already carries the status code and message. For a larger API I would introduce a `@RestControllerAdvice` to centralise error shaping."

This kind of answer shows you understand trade-offs, not just syntax.

## Common Mistakes to Avoid

- **Hardcoded credentials in source code.** Even in a demo, `password=root123` in a committed file will be noticed and flagged by any experienced reviewer.
- **No README.** A cloned repo that fails silently because the database was never created signals poor communication skills.
- **One massive initial commit.** Squash conflicts or rebase if needed, but try to preserve logical milestones in the history.
- **Leaving `ddl-auto=create-drop` in production configuration.** Set it to `validate` or `none` before sharing; reviewers will notice and question whether you understand data lifecycle.
- **Broken `main` branch.** Always verify the app starts from a fresh clone before sending the link.

## A Quick Checklist Before Sharing

```
[ ] git log looks intentional — meaningful messages, logical progression
[ ] README covers: what it does, stack, how to run, main endpoints
[ ] No passwords, tokens, or .env files tracked
[ ] App starts with ./mvnw spring-boot:run after the documented setup
[ ] At least one meaningful test passes with ./mvnw test
[ ] spring.jpa.show-sql is false or removed (noisy in production)
```

---

A well-presented project communicates competence before the interview even begins. Clean history, a clear README, and the ability to explain your choices out loud will set you apart from candidates who only built the code but never thought about sharing it.
