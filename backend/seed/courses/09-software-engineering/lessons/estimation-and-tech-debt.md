# Estimation, Technical Debt, and Documentation

Shipping good software requires more than writing clean code. Teams must estimate work accurately enough to plan, manage the accumulation of shortcuts, and document enough so that knowledge survives beyond any single engineer's tenure.

## Software Estimation

Estimation is notoriously difficult. Humans are inherently optimistic; software is complex; requirements change. Despite this, teams must plan — stakeholders need release dates, budgets, and priorities. The goal of estimation is not a perfect prediction but a shared understanding of complexity that supports decision-making.

### Why Estimates Are Hard

- **Unknown unknowns:** Hidden complexity only surfaces when you start coding ("the API we're integrating doesn't support that feature we assumed")
- **Interruptions:** Meetings, bug fixes, on-call duties reduce actual coding time by 30–50%
- **Integration surprises:** Combining components often takes longer than building them
- **Requirement drift:** What you're asked to build changes mid-development
- **Optimism bias:** Developers consistently underestimate their own tasks by a factor of 2–3×

The **planning fallacy** (Kahneman & Tversky, 1979): people systematically underestimate costs and durations while overestimating benefits, even when they know similar past projects went over schedule.

### Estimation Techniques

**Planning Poker** (relative sizing with story points):
1. Product Owner reads the story and answers questions
2. Each team member privately picks a Fibonacci card (1, 2, 3, 5, 8, 13, 21)
3. All reveal simultaneously
4. Outliers explain their reasoning — divergence reveals hidden complexity
5. Re-estimate until consensus (or majority vote after two rounds)

Fibonacci numbers are used deliberately: the gaps grow larger as complexity increases, making it harder to obsess over the difference between 7 and 8 when the real question is "is this a 5 or a 13?"

**Three-Point Estimation** (for tasks where hours matter):
```
Estimate = (Optimistic + 4 × Most Likely + Pessimistic) / 6

Example:
  Optimistic  (O) = 2 hours  (everything goes perfectly)
  Most Likely (M) = 5 hours  (normal progress)
  Pessimistic (P) = 14 hours (third-party API is broken, tests reveal new requirements)

  Estimate = (2 + 4×5 + 14) / 6 = (2 + 20 + 14) / 6 = 36 / 6 = 6 hours

Standard deviation = (P - O) / 6 = (14 - 2) / 6 = 2 hours
```

The standard deviation gives you a confidence range: the estimate is likely between 4 and 8 hours.

**Reference class forecasting:** Instead of estimating from scratch, look at how long similar past tasks took. If "add OAuth login" took 3 days last time, that is a better estimate for this one than a fresh analysis suggests.

**#NoEstimates approach:** Track cycle time (time from "started" to "done") for completed stories, categorised by size (S/M/L). Use historical data to forecast: "medium stories take 2–4 days on average; we have 8 of them; expect 16–32 days."

### Common Estimation Mistakes

- Estimating in calendar time instead of effort (a task takes 8 hours of work, not 8 calendar hours when interruptions exist)
- Not accounting for code review, testing, CI debugging, and deployment time (these can double the development time)
- Letting "feature creep" add scope after the estimate was locked
- Not splitting large stories before estimating (stories > 8 points are usually too vague to estimate accurately)
- "Padding" estimates secretly instead of discussing uncertainty openly with stakeholders

## Technical Debt

**Technical debt** is the implied cost of rework caused by choosing an easier but worse solution now. Ward Cunningham coined the term in 1992 as a deliberate financial metaphor: shortcuts are a loan that accrues interest in the form of slower future development.

### Types of Technical Debt (Fowler's Quadrant)

|  | Reckless | Prudent |
|---|---|---|
| **Deliberate** | "We don't have time for design" | "We must ship now; we'll fix the design later" |
| **Inadvertent** | "What's layered architecture?" | "Now we know we should have used CQRS" |

- **Deliberate/Reckless:** The worst kind. Team knows it is wrong but doesn't care.
- **Deliberate/Prudent:** Conscious shortcut with a plan to fix later. Acceptable if the "later" is tracked and scheduled.
- **Inadvertent/Prudent:** Team learns from building; now they understand the better approach. Common and normal.
- **Inadvertent/Reckless:** Team writes bad code without knowing it's bad. Fixed by training, code review, and pairing.

### Recognising Technical Debt

Signs that debt is accumulating:
- Features that "should be simple" take disproportionately long
- Developers are afraid to touch certain parts of the codebase ("the magic auth module")
- New team members take weeks to be productive because nothing is documented or consistent
- Bug fixes frequently introduce new bugs in unrelated areas
- Test coverage below 40% in critical modules

### Managing Technical Debt

- **Make it visible:** use a tech debt register (a dedicated board column, a tag in your issue tracker, or a `TECH_DEBT.md` file)
- **Schedule repayment:** allocate 10–20% of each sprint to debt reduction — treat it like backlog work, not extra-curricular
- **Stop accumulating:** enforce code review standards that reject avoidable shortcuts; "we'll fix it later" is only acceptable when later is a dated ticket
- **Prioritise ruthlessly:** address debt that blocks new features or causes production incidents first
- **Refactoring sprints:** occasionally dedicate a full sprint to infrastructure/quality work — communicated to stakeholders as "engineering health investment"

The danger of ignoring technical debt is that it compounds: each new feature built on a shaky foundation becomes harder to add, test, and maintain.

## Technical Documentation

Good documentation multiplies a team's effectiveness by allowing knowledge to be shared asynchronously — across time zones, across employee tenure, and across memory loss.

### Types of Documentation

| Type | Purpose | Owner | Format |
|---|---|---|---|
| README | Getting started, project overview | Engineering | Markdown |
| Architecture doc / ADR | Major design decisions | Tech lead | Markdown |
| API reference | Every endpoint, parameter, response | Auto-generated | OpenAPI / Swagger |
| Runbook | Step-by-step ops procedures ("how to restart the worker", "how to clear a stuck queue") | SRE / DevOps | Markdown in `docs/runbooks/` |
| Post-mortem | What went wrong and how to prevent recurrence | On-call lead | Shared doc / wiki |
| Onboarding guide | How to set up a local dev environment | Engineering | Markdown |

### The Docs-as-Code Approach

Store documentation alongside code in the repository. Review documentation changes in PRs just like code changes. Generate documentation from code where possible (docstrings → Sphinx, FastAPI routes → OpenAPI, SQL schema → dbdocs).

**Benefits:**
- Documentation changes with the code that it describes — reviewers catch stale docs just as they catch bugs
- Version history shows why documentation changed, not just that it changed
- Docs can be linted, spell-checked, and link-validated in CI

### The Diataxis Framework

Divio's Diataxis framework categorises documentation into four types:

| Type | Answers | Example |
|---|---|---|
| **Tutorial** | "How do I get started?" | "Build your first API in 10 minutes" |
| **How-to guide** | "How do I do X?" | "How to add OAuth login" |
| **Reference** | "What does X do?" | API endpoint documentation |
| **Explanation** | "Why does this work this way?" | "Why we chose PostgreSQL over MongoDB" |

Mixing these types in one document confuses readers. A common mistake: writing a tutorial (step-by-step) as if it is a reference (complete description of options). Separate them.

### Writing Good Documentation

- **Audience first:** write for someone joining the team next month, not for yourself today
- **Show, don't just tell:** examples and code snippets beat prose descriptions
- **Short and scannable:** use headers, bullet lists, code blocks — people skim technical docs
- **Link, don't duplicate:** link to authoritative sources rather than copying content that will drift out of sync
- **Explain the why:** future maintainers need to understand decisions, not just the current state
- **Date when necessary:** post-mortems and RFCs benefit from dates; API references should be tied to version numbers
