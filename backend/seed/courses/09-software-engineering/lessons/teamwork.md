# Teamwork and Engineering Culture

Software is almost always built by teams. Technical skill is necessary but not sufficient — how a team communicates, resolves disagreements, shares knowledge, and handles failure determines whether great engineers produce great software or mediocre software that barely ships.

## Conway's Law

> "Organizations which design systems are constrained to produce designs which are copies of the communication structures of those organizations."
> — Melvin Conway, 1968

If three teams own separate services, those services will reflect the boundaries between teams — including the friction. A team that communicates poorly will produce a poorly integrated system. Before choosing a microservices architecture, ask whether your org structure supports it.

**Inverse Conway Maneuver:** intentionally organise teams to match the architecture you want. If you want loosely coupled, independently deployable services, form cross-functional teams that each own one service end-to-end — frontend, backend, database, and deployment.

## Blameless Post-Mortems

When a production incident occurs, teams that blame individuals produce two bad outcomes: the blamed person feels unsafe and is less likely to escalate problems in the future, and the root cause goes unfixed because the *system* that allowed the incident is not examined.

A **blameless post-mortem** assumes everyone acted with the best intentions and the best information they had at the time. It asks:

1. **What happened?** (Timeline of events with exact timestamps)
2. **Why did it happen?** (Root cause analysis using "5 Whys" technique)
3. **What is the impact?** (Users affected, revenue lost, time to recovery)
4. **What prevented us from detecting it sooner?**
5. **What actions will we take to prevent recurrence?** (Each action has an owner and a deadline)

Post-mortems are shared with the whole engineering organisation — they are learning opportunities, not punishments. Google publishes a subset of its production post-mortems externally; this culture of radical transparency accelerates organisational learning.

### The 5 Whys Example

```
Incident: API returned 500 errors for 12 minutes on 2024-03-15

Why 1: The database ran out of connections.
Why 2: A new background job was opening DB connections without closing them.
Why 3: The job used a raw psycopg2 connection instead of our connection pool.
Why 4: The job was written by a contractor who was unfamiliar with our patterns.
Why 5: We have no onboarding guide or code example for background jobs.

Root cause: Missing documentation caused a new contributor to bypass the
connection pool.

Action: Write a background job guide with code examples (Alice, by 2024-03-22).
Action: Add a linter rule that warns when psycopg2 is imported directly (Bob, 2024-03-29).
```

## On-Call and Incident Management

Teams that build a service should own operating it ("you build it, you run it"). On-call rotations share the operational burden fairly:

- Each engineer takes a rotation (e.g., one week per month, paired with a secondary)
- Alerts are documented with runbooks: "What does this alert mean? What should I do?"
- Rotations are reviewed for fairness — no one should be on-call most of the time

**Good incident management practices:**
- **Incident commander:** one person drives the response and makes decisions; others execute tasks or observe. Avoiding two people trying to "fix" the same thing simultaneously.
- **Communication channel:** all updates in a single channel (dedicated Slack channel or PagerDuty timeline) so the whole team knows the current state
- **Status page:** update customers proactively — silence breeds distrust
- **No side-investigations during the incident:** fix the problem first, understand why afterwards

## Psychological Safety

Google's Project Aristotle (2016) studied 180 teams over two years and found that **psychological safety** — the shared belief that the team is safe for interpersonal risk-taking — was the strongest predictor of team effectiveness, above all other factors (including talent, structure, and resources).

Teams with psychological safety:
- Surface problems earlier (before they become production incidents)
- Propose unconventional solutions without fear of ridicule
- Admit when they don't know something rather than guessing
- Give honest feedback in code review without personal attacks
- Experiment and learn from failures rather than avoiding anything risky

Building psychological safety requires consistent behaviour from technical leads and managers:
- Thank people for raising problems, especially uncomfortable ones
- Never publicly humiliate or mock a teammate's mistake
- Separate critical feedback from personal criticism: "This function has three responsibilities" not "You always write messy code"
- Model vulnerability: admit your own uncertainty and mistakes

## Developer Productivity

Developers are most productive when they have:

- **Flow time:** blocks of 2+ hours of uninterrupted focus. Interruptions (Slack, meetings) break cognitive work disproportionately — it takes 20–30 minutes to regain deep focus after an interruption.
- **Fast feedback loops:** CI that runs in under 10 minutes, hot-reload in local dev, same-day code review
- **Good tooling:** IDE with autocomplete and type checking, linters/formatters that run automatically, a local dev environment that starts in one command
- **Clear goals:** understanding *why* the story matters, not just what to build

### DORA Metrics

The **DORA metrics** (DevOps Research and Assessment) are the industry-standard measures of engineering delivery performance:

| Metric | Elite performers | High | Medium | Low |
|---|---|---|---|---|
| Deployment frequency | Multiple times/day | Once/day–week | Once/week–month | < Once/month |
| Lead time for changes | < 1 hour | 1 day–1 week | 1 week–1 month | > 1 month |
| Change failure rate | 0–5% | 5–10% | 10–15% | > 15% |
| Mean time to restore | < 1 hour | < 1 day | < 1 week | > 1 week |

(Source: DORA State of DevOps Report 2023)

Elite teams deploy frequently, fail rarely, and recover quickly when they do fail. These metrics correlate with both software quality and team well-being.

## Effective Async Communication

Engineers lose disproportionate amounts of time to poorly run or unnecessary synchronous meetings:

**Async-first principles:**
- Write it down before scheduling a meeting: can this be a document that people comment on?
- Every meeting has an agenda, an owner, and a time limit — circulated in advance
- Decision meetings end with a documented decision posted to a channel or document
- Recurring ceremonies (standups, retros) are time-boxed and facilitated, not free-form
- Recorded demos and written proposals replace synchronous presentations when the audience is distributed

**The "1 pager" culture:** for any significant proposal (technical or process), write a one-page summary with context, options, and a recommendation. Circulate it asynchronously. Discuss only the unresolved questions. This scales far better than decisions-by-meeting as teams grow.
