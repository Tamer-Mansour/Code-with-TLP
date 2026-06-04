# Testing Strategies: Equivalence Partitioning, Boundary Analysis, and Coverage

Effective testing is not about running as many tests as possible — it is about running the *right* tests. Two systematic techniques from black-box testing theory help you choose inputs that maximise defect detection per test case: **equivalence partitioning** and **boundary value analysis**.

**Free resource:** *Software Engineering: A Modern Approach* by Marco Tulio Valente — [softengbook.org](https://softengbook.org/) — covers black-box and white-box testing strategies in Chapter 8.

> "Testing can show the presence of bugs, but never their absence." — Edsger W. Dijkstra

This is not pessimism — it is a mathematical fact. The input space of any non-trivial program is effectively infinite; exhaustive testing is impossible. Testing increases confidence but cannot guarantee correctness. The goal is maximum defect coverage per test case written.

## Black-Box vs. White-Box Testing

| Dimension | Black-Box | White-Box |
|---|---|---|
| Basis | Specification / requirements | Source code / internal structure |
| Knowledge needed | What the system should do | How it does it |
| Techniques | Equivalence partitioning, BVA | Statement coverage, branch coverage, path coverage |
| Finds | Missing features, wrong behaviour | Untested code paths, logic errors |

The two approaches are complementary. A complete test strategy uses both.

## Equivalence Partitioning

**Equivalence partitioning** divides the input domain into **equivalence classes** — groups where every member is expected to exercise the same code path and produce the same category of output. If one value in a class reveals a defect, any other value in the same class would too. Testing one representative per class is therefore sufficient to cover the class.

### Example: Age-Based Ticket Pricing

Specification:
```
age < 0          → INVALID
0 <= age <= 12   → CHILD
13 <= age <= 17  → TEEN
18 <= age <= 64  → ADULT
age >= 65        → SENIOR
```

Equivalence classes and representative test values:

| Class | Representative | Expected Output |
|---|---|---|
| age < 0 | −5 | INVALID |
| 0–12 | 7 | CHILD |
| 13–17 | 15 | TEEN |
| 18–64 | 30 | ADULT |
| age ≥ 65 | 70 | SENIOR |

Testing these five values covers all five classes. Testing −1, −500, and −99 would be redundant — they all belong to the same class.

## Boundary Value Analysis

Defects cluster at **boundaries** — the edges of equivalence classes. Off-by-one errors (`<` vs. `<=`), fence-post errors, and range mismatches all manifest at boundaries. **Boundary value analysis (BVA)** supplements equivalence partitioning by testing the values at and immediately around each boundary.

For the age specification, the boundaries are at 0, 12/13, 17/18, and 64/65:

| Boundary | Test values |
|---|---|
| 0 (lower edge of CHILD) | −1, 0, 1 |
| 12/13 (CHILD/TEEN) | 12, 13 |
| 17/18 (TEEN/ADULT) | 17, 18 |
| 64/65 (ADULT/SENIOR) | 64, 65 |

A common formula: for each boundary value `b`, test `b−1`, `b`, and `b+1`. This catches the majority of boundary defects with a minimal number of test cases.

## Statement Coverage

**Statement coverage** (also called line coverage) measures the percentage of executable statements visited by at least one test case.

```python
def classify_score(score):
    if score >= 90:           # Line 1
        return "A"            # Line 2
    elif score >= 80:         # Line 3
        return "B"            # Line 4
    else:
        return "C"            # Line 5
```

A single test `classify_score(95)` achieves 3/5 = 60% statement coverage (lines 1, 2, 3 are executed; lines 4 and 5 are not). To reach 100%, you need at least three tests covering scores ≥90, 80–89, and <80.

Statement coverage is the most common metric reported by tools like `pytest --cov`, but 100% statement coverage does not mean 100% correctness — it only means every line has been executed at least once.

## Branch Coverage

**Branch coverage** (decision coverage) measures the percentage of branches — each `True` and `False` outcome of every condition — exercised by at least one test.

For the `classify_score` function above, there are four branches:
- `score >= 90` evaluates to True → return "A"
- `score >= 90` evaluates to False → proceed to elif
- `score >= 80` evaluates to True → return "B"
- `score >= 80` evaluates to False → return "C"

Branch coverage is strictly stronger than statement coverage: 100% branch coverage implies 100% statement coverage, but not vice versa.

## Test-Driven Development (TDD) and Coverage

TDD's **red-green-refactor** cycle naturally produces high coverage because every line of production code is written to satisfy a failing test:

```
1. RED:    Write a failing test for the next small behaviour
2. GREEN:  Write the minimum code to make the test pass
3. REFACTOR: Clean up code and tests; tests remain green
```

TDD does not mean 100% coverage is the target — it means coverage is a *byproduct* of the process, not a goal to game. Coverage targets (e.g., "80% minimum") in CI pipelines are useful as a safety net, not as a quality benchmark.

## Static Analysis

**Static analysis** finds defects without executing the code. Tools like `pylint`, `flake8`, `mypy` (type checking), and `bandit` (security) catch a wide class of bugs — undefined variables, type mismatches, common anti-patterns — before a single test runs. Static analysis is the cheapest form of automated quality assurance and should be the first gate in any CI pipeline.

## The Testing Hierarchy in Practice

A healthy test strategy combines all these techniques:
1. Static analysis + type checking (catches errors before execution)
2. Unit tests using equivalence partitioning and BVA (fast, isolated)
3. Integration tests (real component boundaries)
4. System / E2E tests for critical user journeys
5. Performance and security tests for NFRs

Coverage reports identify blind spots. Mutation testing (deliberately injecting small bugs to see if tests catch them) goes further — it measures test suite *effectiveness*, not just execution breadth.
