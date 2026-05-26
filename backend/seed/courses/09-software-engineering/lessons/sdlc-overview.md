# The Software Development Lifecycle

The **Software Development Lifecycle (SDLC)** is the structured process a team follows to plan, build, test, and ship software. Understanding it prevents wasted effort, misaligned expectations, and last-minute crises. Choosing the right model for your team and context is one of the highest-leverage decisions an engineering leader makes.

## Why a Process Matters

Without a shared process, developers might code features nobody asked for, testers might find bugs only after shipping, and managers might have no idea whether the product will be ready on time. A lifecycle makes every role's responsibilities explicit and creates checkpoints to catch mistakes early — when they are cheap to fix.

The "cost of change" curve is a well-known principle: fixing a requirements mistake before coding begins costs roughly 1×; fixing it after deployment can cost 100×. This is why the early phases of any SDLC exist.

## Phases of the SDLC

Most models share these core phases, even if they label them differently:

| Phase | Goal | Common Output |
|---|---|---|
| Requirements | Understand what to build | User stories, specs, acceptance criteria |
| Design | Decide how to build it | Architecture diagrams, wireframes, ADRs |
| Implementation | Write the code | Working software, commits, PRs |
| Testing | Verify correctness | Test reports, bug tickets, coverage reports |
| Deployment | Ship to users | Release, change log, deployment pipeline |
| Maintenance | Keep it running | Patches, monitoring dashboards, runbooks |

## Waterfall

Waterfall executes each phase fully before the next begins. A team writes all requirements, then designs everything, then codes everything, then tests everything.

**Strengths:** Clear milestones, easy to manage fixed-price contracts, suits stable requirements where change is expensive.

**Weaknesses:** Users see nothing until the end; changing requirements mid-project is expensive; bugs found in testing may require redesign of entire modules.

Waterfall works well for embedded systems or government contracts where requirements are legally fixed upfront. Safety-critical software (aviation, medical devices) often uses a waterfall variant with formal verification stages.

### A Realistic Waterfall Timeline

```
Month 1–2:   Requirements (SRS document)
Month 3–4:   System design (SDD document)
Month 5–9:   Implementation
Month 10–11: System testing (SIT, UAT)
Month 12:    Deployment
```

Note that in this model, a developer won't write a single line of code for the first four months, and a stakeholder won't see working software until month 12.

## Agile

Agile delivers software in short **iterations** (typically 1–4 weeks) called **sprints**. Each sprint produces a potentially shippable increment. Requirements are allowed to evolve; feedback is gathered continuously.

Key Agile values from the Manifesto (2001):
- Individuals and interactions over processes and tools
- Working software over comprehensive documentation
- Customer collaboration over contract negotiation
- Responding to change over following a plan

The right side of each comparison still has value — Agile doesn't say processes, documentation, contracts, and plans are worthless. It says the left side is *more* valuable.

### Scrum

Scrum is the most popular Agile framework. It defines:

**Artefacts:**
- **Product Backlog** — ordered list of everything the product might need (owned by Product Owner)
- **Sprint Backlog** — subset committed to in the current sprint (owned by Development Team)
- **Increment** — the usable product at the end of each sprint

**Ceremonies:**
- **Sprint Planning** (start of sprint, ≤8h for 4-week sprint): team selects backlog items and creates tasks
- **Daily Standup** (15 min): what did I do yesterday? what will I do today? any blockers?
- **Sprint Review** (4h): demo to stakeholders, collect feedback
- **Sprint Retrospective** (3h): what went well? what should we improve? (focused on process, not product)

**Roles:**
- **Product Owner** — owns the backlog, represents stakeholder interests, makes priority decisions
- **Scrum Master** — coaches the process, removes impediments, protects the team from distractions
- **Development Team** — self-organising, cross-functional (developers, testers, designers)

### A Sprint in Practice

```
Day 1:      Sprint Planning — select 32 points from backlog
Days 2–13:  Development — daily standups, coding, review
Day 14 AM:  Sprint Review — demo to stakeholders
Day 14 PM:  Sprint Retrospective — improve the process
            → Sprint Velocity recorded: 29 points completed
```

### Kanban

Kanban is a flow-based approach. Work items move through columns on a board:

```
Backlog → Ready → In Progress → Code Review → Testing → Done
```

There is no fixed sprint; instead, the team limits **Work In Progress (WIP)** per column to prevent bottlenecks. If "In Progress" has a WIP limit of 3 and all three slots are full, no new item can be started until one finishes. This surfaces bottlenecks visually and forces the team to swarm on blocked work.

Kanban is great for teams with unpredictable incoming work (e.g., support or operations) or for teams whose flow needs optimising rather than their planning.

**Key Kanban metrics:**
- **Cycle time** — how long an item takes from "started" to "done"
- **Throughput** — how many items are completed per week
- **CFD (Cumulative Flow Diagram)** — visualises WIP over time; rising WIP bands signal bottlenecks

## Scrum vs Kanban at a Glance

| Aspect | Scrum | Kanban |
|---|---|---|
| Cadence | Fixed sprints (1–4 weeks) | Continuous flow |
| Change mid-cycle | Not during sprint | Any time |
| Roles | PO, SM, Dev Team | No prescribed roles |
| Metrics | Velocity (points/sprint) | Cycle time, throughput |
| Best for | Product teams with planned features | Ops, support, unpredictable flow |
| Planning horizon | Sprint at a time | Rolling |

## SAFe and Scaled Agile

Large organisations (hundreds of developers) often adopt **SAFe (Scaled Agile Framework)** to coordinate multiple Scrum teams. SAFe adds:
- **Program Increment (PI) Planning** — cross-team planning event held every 8–12 weeks
- **Agile Release Trains (ARTs)** — groups of teams that plan and ship together

SAFe is controversial: critics argue it adds bureaucracy that defeats Agile's purpose. The key insight is that scaling Agile is fundamentally harder than scaling code — it requires organisational change, not just process documentation.

## Choosing a Model

No single model fits every team. Consider:

- **Team size:** Scrum works well for 5–9 people. Larger teams need coordination layers (SAFe, LeSS).
- **Requirement stability:** Waterfall or iterative waterfall for fixed-spec projects; Agile for exploratory products.
- **Customer proximity:** Agile needs regular feedback; if your customer is inaccessible, Agile loses its advantage.
- **Regulatory constraints:** Regulated industries (medical devices, aerospace, finance) may mandate documentation artefacts that align better with waterfall phases.

The most important thing is **transparency**: everyone knows the current state of the work, who owns each item, and what "done" means.
