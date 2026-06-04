# Exercise: Docker Compose Dependency Resolver

Apply your knowledge of Docker Compose's `depends_on` configuration by simulating the startup ordering algorithm.

## Background

In a `docker-compose.yml`, services can declare dependencies:

```yaml
services:
  nginx:
    depends_on:
      - app
  app:
    depends_on:
      - api
      - db
  db: {}
  redis: {}
  api:
    depends_on:
      - redis
      - db
```

Docker Compose starts services in **dependency order**: a service only starts after all the services it `depends_on` have started. If multiple services are ready to start simultaneously, Compose may start them in any order.

This ordering problem is a classic **topological sort**. Compose does not guarantee alphabetical order among simultaneously-ready services, but for this exercise we use alphabetical order as a deterministic tiebreaker.

## What You'll Practice

- Implementing Kahn's algorithm (BFS-based topological sort)
- Detecting circular dependency graphs
- Alphabetical tie-breaking in topological ordering

## Further Reading

- **Docker Official Documentation — Compose**: [https://docs.docker.com/get-started/](https://docs.docker.com/get-started/)
- **Play with Docker Classroom**: [https://training.play-with-docker.com/](https://training.play-with-docker.com/) has interactive Compose labs.
