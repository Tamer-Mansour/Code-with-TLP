# Code Review: Giving and Receiving Feedback

Code review is the practice of having another developer examine your changes before they are merged. Done well, it is one of the most powerful quality and knowledge-sharing tools a team has. Done poorly, it is a bottleneck that demoralises authors and lets bugs through anyway.

## Why Code Review Matters

- **Defect detection:** Studies (Fagan 1976, McConnell's *Code Complete*) show code review catches 60–90% of defects before testing — more effective than any other single quality technique.
- **Knowledge sharing:** Reviewers learn about parts of the codebase they don't own; authors learn patterns and constraints they hadn't encountered.
- **Consistency:** Style, architecture, and naming decisions stay aligned across the team without a central "gatekeeper."
- **Collective ownership:** When multiple people review code, no single developer becomes a single point of failure for understanding a module.
- **Security:** A second pair of eyes catches SQL injection, missing auth checks, and hardcoded secrets before they reach production.

## What to Look For as a Reviewer

### 1. Correctness

- Does the code do what the PR description claims?
- Are edge cases handled? (empty list, null input, zero, negative numbers, concurrent access)
- Are errors handled and propagated correctly — or silently swallowed?
- Does the logic match the acceptance criteria in the linked ticket?

```python
# Missed edge case: what if items is empty?
def get_most_expensive(items):
    return max(items, key=lambda x: x.price)   # raises ValueError on empty list

# Fixed
def get_most_expensive(items):
    if not items:
        return None
    return max(items, key=lambda x: x.price)
```

### 2. Design

- Does the change fit the existing architecture? (No database calls in route handlers if you use a service layer)
- Is there duplicated logic that should be extracted?
- Are abstractions at the right level? (Not too generic, not too specific)
- Does this create hidden coupling between modules that should be independent?

### 3. Testing

- Are there tests for the new behaviour?
- Do tests cover failure paths and edge cases, not just the happy path?
- Are tests readable enough to serve as documentation of intent?
- Are new tests actually testing the right thing, or testing implementation details that will break on every refactor?

### 4. Security

- Is user input validated and sanitised before use in queries or shell commands?
- Are any secrets or credentials committed? (Should be zero — secrets in `.env`, not in code)
- Are permissions checked before performing sensitive actions?
- Does the change introduce any new attack surface (new endpoint without auth, new file upload without type validation)?

### 5. Performance

- Any obvious N+1 queries? (Fetching a list, then querying per item in a loop)
- Unbounded loops over large datasets without pagination?
- Missing database indexes for new query patterns?
- Loading large objects into memory that could be streamed?

```python
# N+1 example — spotted in review
orders = db.query(Order).all()
for order in orders:
    user = db.query(User).get(order.user_id)   # N queries!
    print(f"{user.name}: {order.total}")

# Fixed with JOIN
orders = db.query(Order).options(joinedload(Order.user)).all()
for order in orders:
    print(f"{order.user.name}: {order.total}")   # 1 query
```

## How to Give Feedback Constructively

The **tone** of review comments matters as much as their content. Reviewers wield significant power; use it to teach, not to judge.

**Label comments by severity:**

```
# [nit] Consider naming this `user_count` instead of `cnt` for clarity.
# (optional — author's choice)

# [suggestion] This loop runs a query for each user — that's an N+1.
# A single JOIN or prefetch would reduce it to one query.
# (should fix, but author decides)

# [question] Why is this hard-coded to 5? Is it a domain rule or configuration?
# (I'm confused; please explain or extract to a named constant)

# [blocking] This stores the password in plaintext. Must use bcrypt before merging.
# (must fix — merge blocked)
```

**Be specific and actionable.** Point to the exact line. Explain the problem. Suggest a fix:

```
# Bad: "This is a mess."
# Bad: "Wrong."
# Bad: "Why would you do this?"

# Good:
"This function handles both validation and database persistence (two responsibilities).
Extracting the validation into `validate_order(order)` would make both parts easier
to test and would match the pattern we use in `create_user()`. Happy to chat if
the design is unclear."
```

Phrase suggestions as questions when you're not sure: "Could we use a dictionary lookup here instead of 5 `if/elif` branches? I think it might be more readable, but you know this domain better."

Separate **subjective style** ("I'd write it differently") from **objective correctness** ("this will raise a KeyError on empty input"). Only block on correctness issues, security issues, and clear violations of team standards.

## How to Receive Feedback

- Treat review comments as feedback on the code, not on you. The code is not your identity.
- Respond to **every** comment — either fix it, explain why you disagree, or ask a clarifying question. Don't leave comments unacknowledged.
- Don't merge until all blocking items are resolved.
- If you disagree with a suggestion, say so clearly and explain your reasoning: "I considered that, but the dictionary approach requires maintaining an additional mapping that changes independently of this logic. I think the `if/elif` is actually less surprising here. Happy to discuss."
- Thank reviewers for good catches — positive reinforcement improves review culture.
- If a reviewer's comment reveals a misunderstanding of the codebase, consider adding a comment or updating the documentation rather than just fixing the code.

## The Author's Checklist Before Requesting Review

- [ ] PR description explains *what* changed and *why* (links to ticket)
- [ ] PR is small: aim for < 400 lines changed; split large features into stacked PRs
- [ ] Tests pass locally; CI is not already red from a previous run
- [ ] No debug code, commented-out code, `print()` statements left in
- [ ] No `TODO: fix later` without a linked ticket
- [ ] Self-reviewed: read the full diff yourself before assigning reviewers

**Self-review tip:** read your diff in the GitHub/GitLab UI, not in your IDE. You will see it with fresh eyes and catch at least one issue you'd miss otherwise.

## Code Review Anti-Patterns

| Anti-pattern | Problem | Fix |
|---|---|---|
| Rubber-stamping | Approve without reading — bugs slip through | Block merges until CI passes; require substantive comments |
| Nit-picking only | Miss real design/correctness issues | Use a mental checklist: correctness, design, tests, security |
| Review by committee | 5+ reviewers, no clear owner, nothing gets merged | One required approver; others optional |
| Ghost reviewer | Assigned but never responds | 24-hour turnaround policy; ping after 24 hours |
| Late review | PR sits unreviewed for days | Treat unreviewed PRs as WIP that blocks progress |
| Drive-by blocking | Minor stylistic blocks prevent merge | Enforce a linter/formatter; nits are never blocking |

Aim for a **24-hour turnaround** on reviews. Unreviewed PRs are WIP — they cause merge conflicts, context switching for the author, and blocked sprint items.

## Worked Example: A Real Review Exchange

**PR description:** "Add endpoint to soft-delete users"

**Reviewer comment (blocking):**
```
auth/users.py line 47:
The DELETE /users/{id} endpoint doesn't check if the requesting user has
admin privileges. Any authenticated user can delete any other user.
Add a `require_role("admin")` dependency or check `current_user.role == "admin"`
before the deletion. See how we handle this in auth/posts.py line 82.
```

**Author response:**
```
Good catch — I missed that entirely. I've added the admin check using the
`require_role` dependency (same pattern as posts.py). New commit: 3a1f92b.
Also added a test case for the 403 response in test_users.py.
```

This exchange exemplifies good review culture: a specific, actionable blocking comment; a constructive response that fixes the issue, explains what was done, and adds a test.

## Pair Programming as Continuous Review

Pair programming (two developers, one computer) is an alternative to async review. One person "drives" (types), the other "navigates" (thinks about design and spots mistakes). The output is reviewed code by definition.

Research (Williams et al., 2000) shows pairs produce roughly the same defect density as solo developers whose code is reviewed asynchronously — at roughly the same total engineering cost. The difference: pair programming produces the feedback in real-time rather than hours or days later.
