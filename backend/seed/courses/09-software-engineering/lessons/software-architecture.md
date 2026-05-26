# Software Architecture and Design Documents

Architecture is the set of high-level decisions that are hard to change later: how systems are divided, how they communicate, and which technologies are chosen. Getting these right early saves enormous effort. Getting them wrong early commits you to years of expensive workarounds.

## What Architecture Decisions Cover

Architecture sits at the intersection of technical constraints and business goals. The key decision areas:

- **Decomposition:** Monolith vs microservices vs serverless — how many independently deployable units?
- **Communication:** REST, gRPC, message queues (Kafka, RabbitMQ), GraphQL — synchronous or asynchronous?
- **Data stores:** Relational vs document vs key-value vs graph; which specific database and why?
- **Cross-cutting concerns:** How is authentication handled? Centralised logging? Rate limiting? Caching?
- **Consistency model:** Is strong consistency needed, or is eventual consistency acceptable?
- **Failure handling:** What happens when a downstream service is unavailable?

## Common Architectural Patterns

### Layered (N-Tier)

The classic web application structure:

```
┌─────────────────────────────────┐
│  Presentation Layer             │  ← HTTP routes, serialization (FastAPI/Express)
├─────────────────────────────────┤
│  Application / Service Layer    │  ← Business logic, use cases
├─────────────────────────────────┤
│  Domain Layer                   │  ← Domain models, business rules
├─────────────────────────────────┤
│  Data Access Layer              │  ← Repository pattern, ORM (SQLAlchemy)
└─────────────────────────────────┘
```

Simple to understand and teaches, but can become tightly coupled if lower-layer details (ORM model shapes, SQL types) leak into upper layers. The fix is the **Repository pattern**: the service layer only knows about a `UserRepository` interface, never about SQL.

### Microservices

Each bounded domain becomes an independent service with its own database and deployment pipeline. Services communicate via HTTP/REST or async messaging.

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Users   │────▶│  Orders  │────▶│ Payments │
│  Service │     │  Service │     │  Service │
│  :5001   │     │  :5002   │     │  :5003   │
└──────────┘     └──────────┘     └──────────┘
     │                 │                │
  Postgres           MongoDB         Postgres
```

**Pros:** Independent scaling, technology heterogeneity, smaller blast radius, independent deployment cadences.

**Cons:** Distributed system complexity, network latency, harder debugging, no cross-service transactions (requires sagas or eventual consistency), operational overhead (each service needs logging, monitoring, CI/CD, secrets management).

**Start with a monolith.** Microservices only pay off once you have clear service boundaries and separate teams that can own them. Splitting a monolith into microservices prematurely creates a "distributed monolith" — all the complexity of microservices with none of the benefits.

### Event-Driven

Services emit events to a broker; other services subscribe and react. Decouples producers from consumers completely.

```
Order Service                Kafka                  Inventory Service
      │                        │                          │
      │── OrderPlaced event ──▶│                          │
      │                        │──── OrderPlaced ────────▶│ (adjust stock)
      │                        │                          │
      │                        │── InventoryUpdated ─────▶ Analytics Service
```

Good for: workflows where steps happen asynchronously (order → inventory → payment → fulfilment), audit logs, fan-out notifications, loose coupling between teams.

**Challenge:** debugging "what happened?" requires distributed tracing. Event ordering and exactly-once delivery require careful broker configuration.

## Architecture Decision Records (ADRs)

An **ADR** documents a single architecture decision. Stored in the repository, they give future developers context for why the codebase is structured the way it is.

```markdown
## ADR-005: Use PostgreSQL as the primary database

**Status:** Accepted  
**Date:** 2024-03-10  
**Deciders:** Alice Chen, Bob Martinez

### Context

We need a relational store with strong ACID guarantees for financial
transactions. We evaluated: PostgreSQL, MySQL, MongoDB, and CockroachDB.

### Decision

Use PostgreSQL 15. Reasons:
- Strong ACID compliance is non-negotiable for payment records
- JSONB columns support semi-structured event data without a separate doc store
- Row-level security supports our multi-tenant data model
- Team has existing expertise in PostgreSQL

### Consequences

- Dev and CI environments must run PostgreSQL (Docker Compose provided)
- Adds ~50 MB overhead vs SQLite in local dev
- Enables future use of full-text search, PostGIS, and pg_partman

### Alternatives Considered

**MongoDB:** Rejected — lacks multi-document transactions in our use case.
**CockroachDB:** Rejected — adds distribution complexity we don't yet need.
```

Store ADRs in `docs/adr/ADR-NNN-title.md`. Number them sequentially. Never delete an ADR — if a decision is reversed, create a new ADR that supersedes it and update the old one's status to "Superseded by ADR-012."

## UML Basics

UML (Unified Modeling Language) provides a standard visual vocabulary. You rarely need all 14 diagram types. The three most practically useful:

### Class Diagram

Shows classes, attributes, methods, and relationships (inheritance, composition, association).

```
┌──────────────────┐          ┌──────────────────┐
│      User        │  1    *  │      Order       │
│──────────────────│◄─────────│──────────────────│
│ id: int          │          │ id: int          │
│ email: str       │          │ user_id: int     │
│ created_at: date │          │ total: Decimal   │
│──────────────────│          │ status: str      │
│ login()          │          │──────────────────│
│ reset_password() │          │ place()          │
│ is_active()      │          │ cancel()         │
└──────────────────┘          └──────────────────┘
```

### Sequence Diagram

Shows how objects interact over time — essential for documenting API flows and async interactions.

```
Client          API Gateway     Auth Service    Database
  │                 │               │              │
  │ POST /login     │               │              │
  │────────────────▶│               │              │
  │                 │ verify token  │              │
  │                 │──────────────▶│              │
  │                 │◀──── ok ──────│              │
  │                 │                   SELECT user │
  │                 │──────────────────────────────▶│
  │                 │◀────────── user row ──────────│
  │◀── 200 + JWT ───│               │              │
```

### C4 Model

A modern, pragmatic alternative to full UML invented by Simon Brown. Four zoom levels:

1. **System Context (L1):** Your system as a single box, surrounded by users and other systems it interacts with
2. **Container (L2):** The deployable units inside your system (web app, API, database, message broker, batch job)
3. **Component (L3):** The major logical components inside one container
4. **Code (L4):** Class diagrams — rarely needed; let your IDE generate these

The C4 model uses consistent notation: boxes for software units, lines for relationships, with labels on both. Every diagram has a title, a legend, and a link to the parent level. This makes diagrams self-explanatory without a presentation.

## Designing for Change

Good architecture anticipates that requirements will change:

**Open/Closed Principle:** software entities should be open for extension but closed for modification. Add new behaviour by adding new code, not changing existing code.

**Interface segregation:** depend on narrow interfaces, not fat ones. A `UserRepository` interface with `get_by_id(id)` and `save(user)` is more testable and changeable than one with 20 methods.

**Hexagonal architecture (ports and adapters):** the business logic knows nothing about the infrastructure (database, HTTP, email). Everything external is behind an interface ("port"), with concrete implementations ("adapters") plugged in from outside.

```python
# Port (interface)
class NotificationPort(ABC):
    @abstractmethod
    def send(self, user_id: int, message: str) -> None: ...

# Adapters (implementations)
class EmailAdapter(NotificationPort):
    def send(self, user_id, message): ...  # uses SendGrid

class SlackAdapter(NotificationPort):
    def send(self, user_id, message): ...  # uses Slack API

class NullAdapter(NotificationPort):
    def send(self, user_id, message): pass  # used in tests
```

## Design Documentation Checklist

A good design doc before starting a significant feature:

- [ ] Problem statement and goals (what user need does this address?)
- [ ] Non-goals (what are we explicitly NOT building?)
- [ ] Proposed solution with diagrams (C4 container or sequence diagram)
- [ ] API or data schema changes (with migration strategy)
- [ ] Alternative approaches considered and why they were rejected
- [ ] Security and privacy implications
- [ ] Rollout and migration plan (can we deploy incrementally?)
- [ ] Observability (what metrics / logs / alerts will we add?)
- [ ] Open questions (with owners and resolution deadlines)

Design docs prevent the team from discovering fundamental problems mid-implementation. The best time to argue about whether a design is correct is before any code is written — not during code review.
