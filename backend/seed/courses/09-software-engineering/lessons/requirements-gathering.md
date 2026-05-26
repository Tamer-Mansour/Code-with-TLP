# Gathering Requirements

Requirements define what the software must do and the constraints it must satisfy. Gathering them is arguably the highest-leverage activity in software development — a mistake here multiplies downstream. The cost of fixing a requirements error after deployment can be 100× the cost of catching it before coding begins.

## Functional vs Non-Functional Requirements

**Functional requirements** describe what the system does — specific behaviours and features:
- "Users can upload a profile photo up to 5 MB in JPEG, PNG, or WebP format."
- "The checkout page calculates tax based on the shipping address using state tax tables."
- "The API returns a paginated list of orders sorted by creation date descending."

**Non-functional requirements** (also called quality attributes or "ilities") describe how well the system does it:

| Category | Example |
|---|---|
| Performance | "Search results return in < 200 ms at p99 under 5,000 concurrent users." |
| Security | "Passwords must be hashed with bcrypt (cost factor ≥ 12)." |
| Scalability | "Must handle 10,000 concurrent WebSocket connections." |
| Availability | "99.9% uptime SLA (< 8.7 hours downtime per year)." |
| Usability | "New users must complete onboarding in under 3 minutes." |
| Maintainability | "Test coverage must exceed 80% before any PR is merged." |
| Compliance | "User data must be stored in EU data centres (GDPR Art. 44)." |

Both types are essential. A system that does the right thing but crashes under load is not shippable. Non-functional requirements are the ones most often discovered late — and are expensive to retrofit because they often require architectural changes.

## Elicitation Techniques

Requirements don't arrive complete — you extract them through deliberate techniques:

| Technique | When to use | Caution |
|---|---|---|
| Stakeholder interviews | Early discovery, complex domains | People often say what they do, not what they need |
| User observation (contextual inquiry) | Understanding real workflows | Time-consuming; researcher must not bias behaviour |
| Workshops / JAD sessions | Resolving conflicting requirements | Needs skilled facilitation; loud voices dominate |
| Surveys / questionnaires | Large user populations | Low response rates, surface-level answers |
| Existing system analysis | Replacing legacy software | Existing system may encode bad assumptions |
| Prototyping | Clarifying UI/UX expectations | Stakeholders may treat prototype as the finished product |
| Event storming | Complex domain discovery (DDD) | Requires trained facilitator; large groups |

### The Five Whys

When a stakeholder tells you what they want, ask "why" five times to uncover the actual need:

```
Stakeholder: "We need a PDF report button."
Why? "Because managers need to see monthly totals."
Why? "Because they present them in board meetings."
Why? "Because the board needs to track KPIs."
Actual need: A real-time dashboard visible in presentations.
```

The stakeholder asked for a PDF; the actual need was a shareable real-time view. You built the wrong thing if you stopped at the first answer.

## Writing a Requirements Document

A lightweight requirements document (sometimes called an SRS — Software Requirements Specification) contains:

1. **Purpose** — one paragraph on why the system exists and what problem it solves
2. **Scope** — what is in and out of scope (non-goals are as important as goals)
3. **User roles / personas** — who will use it (end user, admin, API consumer, third-party integrator)
4. **Functional requirements** — numbered list, testable statements (`FR-001`, `FR-002`, ...)
5. **Non-functional requirements** — measurable targets (`NFR-001`, `NFR-002`, ...)
6. **Constraints** — tech stack mandates, legal requirements, deadlines, budget
7. **Assumptions** — things you're assuming to be true (document them so they can be verified)
8. **Open questions** — things still unknown (with an owner and deadline for resolution)

### Properties of Good Requirements

Each requirement should be:
- **Clear** — unambiguous, one interpretation only
- **Complete** — all conditions covered, including edge cases
- **Consistent** — no contradictions with other requirements
- **Testable** — you can write a test or acceptance criterion to verify it
- **Feasible** — achievable within stated constraints

Bad: "The system should be fast."
Better: "The homepage must load in under 1 second on a 10 Mbps connection at p95."

Bad: "The API should handle errors."
Better: "The API must return a 400 status with a JSON error body for all invalid inputs; it must return a 500 status with a correlation ID for all server errors."

## Use Cases vs User Stories

**Use cases** (formal, common in waterfall/UML-based projects) describe a complete interaction between an actor and the system:

```
Use Case: Reset Password
Actor: Registered User
Precondition: User has a registered account
Main Flow:
  1. User navigates to /forgot-password
  2. User enters their email address
  3. System sends a password-reset email with a time-limited token
  4. User clicks the link in the email
  5. System presents a "new password" form
  6. User enters and confirms a new password
  7. System updates the password and logs the user in
Alternate Flows:
  - 3a: Email not found → display "if this email is registered..." message
  - 6a: Passwords don't match → display validation error
Post-condition: User is logged in with the new password
```

**User stories** are lighter-weight and capture the same intent in one sentence with acceptance criteria. Most Agile teams prefer stories; use cases are useful when requirements must be negotiated and signed off as a formal document.

## The Requirements Trap

Common pitfalls to avoid:

- **Gold-plating:** adding features the user never requested because an engineer thought they'd be useful
- **Analysis paralysis:** spending months gathering requirements instead of building anything; build a prototype to test assumptions
- **Assuming requirements are stable:** they will change — design for change by keeping requirements in a living document
- **Ignoring non-functional requirements:** document them explicitly in the SRS; they have architectural implications
- **Requirements by committee:** every stakeholder adds items but nobody owns the prioritisation; the product owner must have the final say

## Agile and "Just Enough" Requirements

In Agile, you don't write every requirement upfront. Instead, you maintain a **product backlog** of user stories and refine the most important ones "just in time" before a sprint begins. This balances thoroughness with speed.

**Backlog refinement** (also called grooming) is a regular ceremony (typically 1–2 hours per week) where the product owner and team:
1. Review upcoming stories
2. Add missing acceptance criteria
3. Split stories that are too large
4. Remove stories that are no longer relevant
5. Re-estimate stories that have changed

A useful rule: define requirements precisely enough that the team can estimate and build the next sprint's stories without a daily conversation with the product owner. If the team constantly needs to re-engage the PO during a sprint, the stories were not refined enough.
