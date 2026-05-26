# User Stories and Acceptance Criteria

A **user story** is a short, plain-language description of a feature from the perspective of the person who will use it. The format keeps teams focused on delivering value rather than implementing technical requirements for their own sake. Mastering user stories is the bridge between what customers need and what engineers build.

## The Classic Template

```
As a <type of user>,
I want <some goal>
so that <some reason>.
```

**Example:**
> As a registered user, I want to reset my password via email so that I can regain access if I forget it.

This single sentence encodes *who* benefits, *what* they need, and *why* it matters — information that is often lost in vague requirements like "add password reset." The "so that" clause is the most valuable and most often skipped part: it tells you the business goal, which helps you decide what to build when scope must be cut.

## INVEST Criteria

Good stories follow the INVEST acronym:

| Letter | Meaning | Bad example | Good example |
|---|---|---|---|
| I | Independent | Story requires Story B to be done first | Each story can be pulled into a sprint alone |
| N | Negotiable | "Must use OAuth" baked in | "User can log in securely" (implementation flexible) |
| V | Valuable | "Refactor database layer" | "User can log in 3× faster after DB refactor" |
| E | Estimable | So vague team can't size it | Team can agree on a point value in planning |
| S | Small | "Build the entire checkout flow" | "User can add one item to cart" |
| T | Testable | "System should be reliable" | "Page loads in < 2 s on 3G" |

When a story fails INVEST, it is a warning sign. A non-independent story suggests a hidden dependency that should become explicit. A non-estimable story usually means the team needs a spike (a time-boxed investigation to reduce uncertainty).

## Acceptance Criteria

Every story needs **acceptance criteria** — the conditions under which the story is "done." These are usually written in **Given / When / Then** format (Gherkin-style):

```gherkin
Given the user is on the login page and has a valid account,
When they enter the wrong password 5 times,
Then their account is locked and they receive a lockout email.
```

A second criterion for the same story:

```gherkin
Given a locked account,
When the user clicks "Unlock my account" in the lockout email,
Then their account is unlocked and they are redirected to the login page.
```

Acceptance criteria serve two purposes:
1. They force the team to think through edge cases **before** writing a line of code.
2. They become the direct basis for test cases — QA turns each criterion into one or more test scenarios.

### Writing Good Acceptance Criteria

- Be specific and measurable: "fast" is not acceptable; "< 200 ms at p95" is.
- Include both happy paths and failure paths.
- One criterion per scenario — don't combine multiple behaviours in one Given/When/Then.
- Avoid implementation details: "When the user submits the form" not "When the POST request hits `/api/login`".

## Epics and Tasks

Stories live inside a hierarchy:

```
Epic → User Story → Task
```

- **Epic:** A large body of work that spans multiple sprints. ("User authentication system")
- **User Story:** A slice of an epic that delivers value independently. ("User can log in with email/password")
- **Task:** A technical sub-step a developer creates during sprint planning. ("Add bcrypt to password comparison", "Write login endpoint test", "Update API docs")

Some teams add a layer above epics: **Initiatives** or **Themes** that represent strategic business goals ("Grow paid subscriber base"). The hierarchy provides a chain of traceability: every line of code connects to a task, which connects to a story, which connects to an epic, which connects to a business goal.

## Story Points and Estimation

Teams assign relative effort estimates called **story points** (often using Fibonacci: 1, 2, 3, 5, 8, 13, 21). Points capture complexity, risk, and uncertainty — they are **not** hours.

Why not hours? Because two developers may estimate the same task differently in hours (skill level, familiarity) but can agree that task A is roughly twice as complex as task B. Relative comparison eliminates the psychological pressure of absolute hour estimates.

**Planning Poker:**
1. Product Owner reads the story and answers questions.
2. Each team member privately selects a card from their Fibonacci deck.
3. All reveal simultaneously.
4. If estimates diverge significantly (e.g., one person says 3, another says 13), those two explain their reasoning.
5. The team discusses and re-estimates.
6. Repeat until consensus or majority vote.

The divergences are often the most valuable part: the 13-pointer might know about a hidden dependency the 3-pointer was unaware of.

**Velocity** is the average number of story points completed per sprint. After 4–6 sprints, velocity stabilises and becomes a reliable forecasting tool:

```
Remaining backlog: 240 points
Team velocity:      40 points/sprint
Sprints remaining:  240 / 40 = 6 sprints (~12 weeks for 2-week sprints)
```

## Splitting Large Stories

Stories larger than half a sprint should be split. Splitting techniques:

| Technique | Example |
|---|---|
| Split by workflow step | "User can add item to cart" + "User can remove item from cart" |
| Split by user role | "Admin can manage users" → "Admin can create users" + "Admin can deactivate users" |
| Split by data variation | "User can pay by card or PayPal" → one story each |
| Split by acceptance criteria | Each Given/When/Then becomes a story |
| Split happy path from edge cases | "User can reset password" + "User with unverified email cannot reset password" |

## Common Pitfalls

- **Writing stories from a system perspective:** "The database should store user records" — no user, no value.
- **Skipping acceptance criteria:** leads to "done" meaning different things to dev and product.
- **Stories too large to finish in a sprint:** split them further — 5–8 stories per sprint is a healthy range.
- **Acceptance criteria become unit tests only:** also need integration and UX checks.
- **Gold-plating stories:** adding features the story never asked for because it "seemed useful."
- **Ignoring the "so that" clause:** when scope must be cut, you need to know which part delivers the core value.

Well-written user stories are the single most important communication artefact between business and engineering. Investing time in writing them well pays back in reduced re-work, better estimates, and clearer test coverage.
