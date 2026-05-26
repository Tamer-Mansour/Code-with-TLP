# Boolean Logic

Every decision a computer makes—whether to branch, loop, or compare—is built on **Boolean logic**: a system of reasoning where every value is either **True** or **False** (1 or 0). Named after mathematician George Boole, who published *The Laws of Thought* in 1854, this algebra forms the mathematical foundation of all digital circuits and every `if` statement you will ever write.

## Boolean Values

Boolean logic has exactly two values:

| Symbol | Meaning | In binary | In Python |
|--------|---------|-----------|-----------|
| `True` / `1` | "yes", on, high voltage | 1 | `True` |
| `False` / `0` | "no", off, low voltage | 0 | `False` |

There is no "maybe" or "sort of"—this binary nature is what makes it so useful for electronics and programming.

## The Three Fundamental Operations

### NOT (Negation)

NOT inverts its single input. If something is True, NOT makes it False, and vice versa.

| A | NOT A |
|---|-------|
| 0 | 1 |
| 1 | 0 |

Python: `not True` → `False`, `not False` → `True`

Analogy: "The light is NOT on" — if the light is on, the statement is False; if it is off, the statement is True.

### AND (Conjunction)

AND is True only when **both** inputs are True. One False input makes the whole expression False.

| A | B | A AND B |
|---|---|---------|
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | 1 |

Python: `True and False` → `False`

Analogy: A bank vault opens only if you have the correct combination **AND** are inside the authorized time window—both conditions must hold.

### OR (Disjunction)

OR is True when **at least one** input is True. Both can be True simultaneously.

| A | B | A OR B |
|---|---|--------|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 1 |

Python: `False or True` → `True`

Analogy: A security alarm triggers if the front door **OR** the back window sensor detects movement. Either one is sufficient.

## Truth Tables

A **truth table** lists every possible combination of inputs and the corresponding output. With *n* inputs, there are **2ⁿ rows**.

- 1 input → 2 rows (only NOT makes sense here)
- 2 inputs → 4 rows (AND, OR, XOR, NAND, NOR all have 4-row truth tables)
- 3 inputs → 8 rows

Truth tables are the standard way to formally define or verify what any Boolean expression does.

## Additional Important Operations

### XOR (Exclusive OR)

XOR is True when the inputs are **different** — exactly one input is True.

| A | B | A XOR B |
|---|---|---------|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

Python: `a ^ b` (bitwise XOR on integers) or `a != b` (for booleans)

Analogy: A light switch controlled by two switches (as in a hallway): flipping either switch toggles the light—the light is on when the switches are in *different* positions.

XOR is crucial in cryptography (XOR encryption, one-time pads) and in building binary adder circuits.

### NAND and NOR

- **NAND** = NOT AND: False only when both inputs are True.
- **NOR** = NOT OR: True only when both inputs are False.

| A | B | NAND | NOR |
|---|---|------|-----|
| 0 | 0 |  1   |  1  |
| 0 | 1 |  1   |  0  |
| 1 | 0 |  1   |  0  |
| 1 | 1 |  0   |  0  |

Remarkably, **NAND alone** (or NOR alone) can build *any* Boolean operation. This property is called **functional completeness** and makes NAND the most commercially important gate in digital hardware. Entire CPUs can be (and historically were) built using only NAND gates.

### Proof That NAND Is Functionally Complete

```
NOT A     =  NAND(A, A)
A AND B   =  NAND(NAND(A, B), NAND(A, B))   [= NOT(NAND(A, B))]
A OR B    =  NAND(NAND(A, A), NAND(B, B))   [= NAND(NOT A, NOT B)]
```

## Boolean Laws (Boolean Algebra)

These algebraic rules let us simplify complex expressions and circuits:

| Law | AND form | OR form |
|-----|----------|---------|
| Identity | `A AND 1 = A` | `A OR 0 = A` |
| Null | `A AND 0 = 0` | `A OR 1 = 1` |
| Idempotent | `A AND A = A` | `A OR A = A` |
| Complement | `A AND (NOT A) = 0` | `A OR (NOT A) = 1` |
| Double negation | `NOT (NOT A) = A` | — |
| Commutative | `A AND B = B AND A` | `A OR B = B OR A` |
| Associative | `(A AND B) AND C = A AND (B AND C)` | same for OR |
| Distributive | `A AND (B OR C) = (A AND B) OR (A AND C)` | `A OR (B AND C) = (A OR B) AND (A OR C)` |

### De Morgan's Laws

These two laws are especially useful in programming for simplifying `if` conditions:

1. `NOT (A AND B)  =  (NOT A) OR (NOT B)`
2. `NOT (A OR B)   =  (NOT A) AND (NOT B)`

**Practical example:** You want to check that a number is valid (between 0 and 100 inclusive).

```python
# Original condition (valid)
is_valid = (x >= 0) and (x <= 100)

# Invalid condition — what you want to negate:
is_invalid = not is_valid
# By De Morgan: NOT(x>=0 AND x<=100) = (NOT x>=0) OR (NOT x<=100)
is_invalid = (x < 0) or (x > 100)
```

Both versions are logically equivalent. De Morgan's laws let you choose the more readable form.

## Boolean Logic in Programming

### Comparison Operators Produce Booleans

```python
5 > 3      # True
5 == 5     # True
5 != 3     # True
5 >= 10    # False
```

Every comparison produces a Boolean, which can then be combined with AND/OR/NOT.

### Short-Circuit Evaluation

Python (and most languages) uses **short-circuit evaluation**:

- `A and B` — if A is False, B is never evaluated (the result must be False).
- `A or B` — if A is True, B is never evaluated (the result must be True).

This is not just an optimization—it enables patterns like:

```python
# Safe: if user is None, the second part is not evaluated
if user is not None and user.age >= 18:
    grant_access()

# Equivalent using short-circuit for defaults
name = user_input or "Anonymous"  # uses "Anonymous" if user_input is empty/None
```

### Compound Conditions in Real Code

```python
age = 20
has_ticket = True
is_vip = False

# Can enter the concert?
can_enter = (age >= 18) and has_ticket
print(can_enter)   # True

# Gets backstage pass?
backstage = can_enter and is_vip
print(backstage)   # False

# Allow entry with either VIP pass or regular ticket?
allow = is_vip or (age >= 18 and has_ticket)
print(allow)       # True

# Check for invalid form input
x = -5
is_valid = not (x < 0 or x > 100)
print(is_valid)    # False
```

## Worked Example: Simplify a Boolean Expression

Simplify: `NOT (NOT A AND NOT B)` using De Morgan's laws.

```
NOT (NOT A AND NOT B)
= NOT(NOT A) OR NOT(NOT B)     ← De Morgan's 1st law
= A OR B                        ← Double negation applied twice
```

So `NOT (NOT A AND NOT B)` is equivalent to `A OR B`. A circuit with NOT gates and an AND gate can be replaced by a single OR gate—saving hardware.

## Common Misconceptions

**"OR means one or the other, not both."**
In everyday English, "or" often implies exclusivity ("coffee or tea, not both"). In Boolean logic, OR means "at least one"—both True simultaneously is fine. The exclusive version is **XOR**.

**"`if x == True:` is equivalent to `if x:`"**
Usually, but not always. `if x:` checks *truthiness*—non-zero numbers, non-empty strings, and non-empty lists are all truthy. `if x == True:` uses Python's `==` operator, which compares to the specific value `True`. These differ when `x` is an integer: `1 == True` is True, but `2 == True` is False, even though `bool(2)` is True.

**"Boolean algebra is only useful in hardware design."**
Every `if` statement, every loop condition, every database query's `WHERE` clause, every access control check—all of these are Boolean expressions. Boolean algebra is the daily language of software logic.

## Key Takeaways

- Boolean logic has exactly two values: True (1) and False (0).
- The three fundamental operations are **NOT**, **AND**, and **OR**; all others derive from them.
- **XOR** is True when inputs differ; **NAND** can implement any Boolean function (functional completeness).
- Truth tables enumerate all possible input combinations—with *n* inputs there are 2ⁿ rows.
- **De Morgan's laws**: `NOT(A AND B) = (NOT A) OR (NOT B)` and `NOT(A OR B) = (NOT A) AND (NOT B)`.
- Short-circuit evaluation means the second operand of AND/OR may not be evaluated.
