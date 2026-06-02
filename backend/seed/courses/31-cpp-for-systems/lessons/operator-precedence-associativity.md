# Operator Precedence and Associativity

Operator precedence determines which operations bind tighter when multiple operators appear in the same expression. Associativity determines the grouping direction when operators have equal precedence. Getting these wrong causes silent logic bugs that are extremely hard to find.

## The Precedence Hierarchy (Subset for Systems Code)

Listed from highest (binds tightest) to lowest precedence:

| Level | Operators | Associativity |
|-------|-----------|---------------|
| 1 (highest) | `::` | Left |
| 2 | `()` `[]` `.` `->` post `++`/`--` | Left |
| 3 | Unary: `+` `-` `!` `~` pre `++`/`--` `*` `&` `(cast)` `sizeof` | Right |
| 4 | `*` `/` `%` | Left |
| 5 | `+` `-` | Left |
| 6 | `<<` `>>` (shift) | Left |
| 7 | `<` `<=` `>` `>=` | Left |
| 8 | `==` `!=` | Left |
| 9 | `&` (bitwise AND) | Left |
| 10 | `^` (bitwise XOR) | Left |
| 11 | `\|` (bitwise OR) | Left |
| 12 | `&&` (logical AND) | Left |
| 13 | `\|\|` (logical OR) | Left |
| 14 | `?:` (ternary) | Right |
| 15 | `=` `+=` `-=` `*=` ... | Right |
| 16 (lowest) | `,` | Left |

## The Most Common Precedence Mistakes

### Mistake 1: `==` binds tighter than `&`

```cpp
uint8_t status = 0x04;

// WRONG — reads as: status & (0x04 == 0) → status & 0 = 0
if (status & 0x04 == 0) { /* never true */ }

// CORRECT — use parentheses
if ((status & 0x04) == 0) { /* works correctly */ }
```

This is the #1 bitwise precedence bug. The comparison operators (`==`, `!=`, `<`, etc.) all rank higher than the bitwise operators (`&`, `^`, `|`).

### Mistake 2: Shift lower than addition

```cpp
int x = 1 + 2 << 3;
// Reads as: (1 + 2) << 3 = 3 << 3 = 24
// Not:       1 + (2 << 3) = 1 + 16 = 17

// Always parenthesize shift expressions
int y = 1 + (2 << 3);  // explicit intent
```

### Mistake 3: Assignment in condition

```cpp
int ch;
// WRONG: == not =, the condition is always false
while (ch == getchar()) { process(ch); }

// CORRECT: assignment inside condition (requires extra parentheses)
while ((ch = getchar()) != EOF) { process(ch); }
// Outer (): assignment has lower precedence than !=
```

The extra parentheses around the assignment suppress the compiler warning and signal intentional assignment.

## Associativity in Practice

Most binary operators are **left-associative** — they group from left to right:

```cpp
int a = 10 - 3 - 2;  // (10 - 3) - 2 = 5, not 10 - (3 - 2) = 9
```

Assignment and ternary are **right-associative**:

```cpp
int a, b, c;
a = b = c = 0;  // right-to-left: (a = (b = (c = 0)))

int x = cond1 ? 1 : cond2 ? 2 : 3;
// right-to-left: cond1 ? 1 : (cond2 ? 2 : 3)
```

## The Golden Rule: When in Doubt, Parenthesize

```cpp
// Ambiguous intent
result = a | b & c ^ d;

// Clear intent — no precedence knowledge required to read
result = a | ((b & c) ^ d);
```

Parentheses are free at runtime and priceless for readability and correctness.

## Useful Mnemonics

- **Multiplication before addition** — just like elementary math.
- **Shifts before comparisons** — `x << 2 > 0` groups as `(x << 2) > 0`.
- **Bitwise before logical** — `a & b && c` groups as `(a & b) && c`.
- **Comparison before bitwise** — the trap: `a & b == 0` groups as `a & (b == 0)`.

## Worked Example: Packet Flag Check

```cpp
uint16_t header = read_network_header();
uint16_t FLAGS_MASK = 0x00FF;
uint16_t VERSION_MASK = 0xFF00;

// Extract and test fields safely
bool is_v2    = ((header & VERSION_MASK) >> 8) == 2;
bool has_data = (header & 0x0001) != 0;
bool is_valid = is_v2 && has_data && ((header & FLAGS_MASK) != FLAGS_MASK);
```

Each sub-expression is parenthesized to make the intent explicit and avoid precedence surprises.

**Interview answer:** "Comparison operators bind tighter than bitwise operators, so `a & b == 0` means `a & (b == 0)` — almost always a bug. The fix is explicit parentheses: `(a & b) == 0`. When writing expressions with mixed operators, always parenthesize to document intent rather than relying on memorized precedence tables."
