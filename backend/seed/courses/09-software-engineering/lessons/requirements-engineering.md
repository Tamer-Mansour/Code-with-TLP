# Requirements Engineering

**Requirements engineering** is the process of discovering, documenting, and managing what a software system must do. It is widely acknowledged that requirements errors are the most expensive class of software defect — mistakes discovered after deployment can cost 50–200× more to fix than mistakes caught during the requirements phase. Getting requirements right is not a bureaucratic formality; it is the highest-leverage activity in software engineering.

**Free resource:** *Introduction to Software Engineering* (Wikibook) — [en.wikibooks.org/wiki/Introduction_to_Software_Engineering](https://en.wikibooks.org/wiki/Introduction_to_Software_Engineering) — covers requirements engineering, use case diagrams, and SRS documents in depth.

## Functional vs. Non-Functional Requirements

**Functional requirements** define what the system *does* — its behaviour, features, and data transformations:

- "Users shall be able to reset their password by providing their registered email address."
- "The system shall display the top 10 best-selling courses on the home page."
- "Administrators shall be able to deactivate user accounts."

**Non-functional requirements (NFRs)** define *how well* the system performs — qualities that constrain the solution space:

| Category | Example |
|---|---|
| Performance | "The search API must respond in < 300 ms at the 95th percentile under 1,000 concurrent users." |
| Availability | "The platform must maintain 99.9% uptime (≤ 8.7 hours downtime per year)." |
| Security | "All passwords must be hashed with bcrypt (cost ≥ 12)." |
| Scalability | "The system must support horizontal scaling to handle 10× traffic spikes." |
| Usability | "A new user shall complete account registration in under 3 minutes without training." |
| Maintainability | "All modules must have unit-test coverage ≥ 80%." |

NFRs are often neglected until a system is in production and failing under load. They should be defined explicitly and verified with measurable acceptance criteria — not left as vague aspirations.

## Elicitation Techniques

Requirements do not arrive fully formed. You must extract them from stakeholders using structured techniques:

**Interviews:** One-on-one conversations with stakeholders. Prepare open-ended questions ("Walk me through how you currently handle X") before moving to closed questions ("Must this happen in under one second?"). Interviews surface context and priorities that documents never capture.

**Workshops / Joint Application Design (JAD):** Facilitated group sessions with multiple stakeholders. Resolve conflicting requirements in real time. Costlier to organise but far faster than serial interviews.

**Observation (ethnographic study):** Watch users perform their actual work. People routinely omit steps they perform automatically and forget to mention workarounds they have normalised. Observation reveals the gap between the described process and the real process.

**Prototyping:** Build a low-fidelity prototype (paper mockup, Figma wireframe, or throw-away code) and use it to elicit reactions. Stakeholders find it far easier to say "that's wrong" when looking at a concrete mockup than to articulate requirements in the abstract.

**Document analysis:** Review existing systems, reports, and policies. Regulatory requirements, existing database schemas, and legacy system outputs are all sources of implicit requirements.

## User Stories

A **user story** is a concise, informal description of a feature from the perspective of the user who benefits from it:

```
As a [role], I want [capability] so that [benefit].
```

Examples:
```
As a student, I want to bookmark lessons so that I can return to them easily.
As an instructor, I want to see completion rates per lesson so that I can identify confusing content.
As an administrator, I want to export user data as CSV so that I can analyse engagement in Excel.
```

**Acceptance criteria** define the conditions that must be true for the story to be considered done. They are written in "Given / When / Then" (Gherkin) format:

```
Given I am logged in as a student
When I click the bookmark icon on any lesson
Then the lesson appears in my Bookmarks list
And the bookmark icon shows as filled/active
```

Well-written acceptance criteria make stories independently testable and eliminate the ambiguity that leads to rework.

## Use Case Diagrams

Use case diagrams (from UML) show the **actors** (users or external systems) and the **use cases** (goals they achieve) in your system, plus the relationships between them.

```
             ┌─────────────────────────────────────────┐
             │            LMS Platform                  │
             │                                          │
 [Student] ──┼──► (Browse Courses)                      │
             │──► (Enrol in Course)                     │
             │──► (Submit Exercise)                     │
             │──► (View Progress)                       │
             │                                          │
[Instructor]─┼──► (Create Course)                      │
             │──► (Publish Lesson)                      │
             │──► (View Analytics)                      │
             │                                          │
             └─────────────────────────────────────────┘
```

Use case diagrams are intentionally high-level — they answer "what can each actor do?" not "how?" They are excellent for communicating scope to non-technical stakeholders.

## Requirements Specification (SRS)

A **Software Requirements Specification (SRS)** is the formal document that records all agreed requirements. A well-structured SRS includes:

1. **Introduction:** purpose, scope, definitions, and references
2. **Overall description:** product perspective, user classes, assumptions, dependencies
3. **Specific requirements:** all functional requirements (often numbered: FR-001, FR-002…) and NFRs
4. **Appendices:** data models, interface prototypes, glossary

Each requirement should be:
- **Unambiguous:** only one interpretation is possible
- **Verifiable:** you can write a test case that confirms it
- **Traceable:** linked to a business goal and eventually to code

## Managing Changing Requirements

Requirements change — in Agile this is expected and embraced; in Waterfall it is managed through a **change control process** (formal request → impact assessment → approval → update). Either way, the team needs:

- A **baseline:** the agreed-upon requirements at a point in time
- A **change log:** every modification, who requested it, and why
- **Traceability matrix:** which requirement is satisfied by which test and which code

Uncontrolled requirements changes ("scope creep") are one of the most common causes of project failure. The antidote is making the cost and impact of every change visible to stakeholders before approval.
