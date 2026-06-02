# Short-Circuit Evaluation and Its Side Effects

Short-circuit evaluation is a fundamental feature of `&&` and `||`. When the result of a logical expression is determined by the left operand alone, the right operand is **not evaluated at all** — not even its side effects.

## How Short-Circuiting Works

- `A && B`: if `A` is `false`, the entire expression is `false`. `B` is never evaluated.
- `A || B`: if `A` is `true`, the entire expression is `true`. `B` is never evaluated.

```cpp
int x = 0;

// Safe null-pointer guard
int* p = nullptr;
if (p != nullptr && *p > 0) {   // *p never evaluated when p is null
    printf("positive\n");
}

// Short-circuit prevents division by zero
int denom = 0;
if (denom != 0 && 100 / denom > 5) {  // division skipped when denom == 0
    printf("big ratio\n");
}
```

## The Sequence Point Guarantee

The C++ standard (and C99) guarantees that the left operand of `&&` and `||` is **fully evaluated** (including all side effects) before the right operand is considered. This is called a *sequence point*.

```cpp
bool is_valid(const char* s) {
    return s != nullptr && s[0] != '\0';  // guaranteed left-to-right
}
```

This guarantee does NOT apply to the bitwise `&` and `|` — both operands are always evaluated in an unspecified order.

## Side Effects in Short-Circuited Expressions

Because the right operand may not execute, embedding side effects there is dangerous:

```cpp
int count = 0;

bool found = search(items, n) || (++count, false);
// If search() returns true, ++count never runs!
// count may not reflect the number of failed searches.
```

This is a maintenance trap. Side effects belong in explicit statements, not inside `||`/`&&` expressions.

### A Legitimate Use: Lazy Initialization

```cpp
static Database* db = nullptr;

bool ensure_connected() {
    return db != nullptr || (db = connect()) != nullptr;
    // Connect only when db is null. Short-circuit prevents re-connect.
}
```

This pattern is common in C-style code but should be used sparingly and commented clearly.

## Ternary Operator and Short-Circuiting

The ternary `?:` also short-circuits: only the selected branch is evaluated.

```cpp
int val = condition ? expensive_true() : expensive_false();
// Only one of the two functions is called
```

This makes ternary useful for lazy evaluation, but again — avoid side effects in non-selected branches.

## Overloaded `&&` and `||` — Short-Circuiting LOST

This is a subtle trap for class authors. If you overload `operator&&` or `operator||` for a class, short-circuit evaluation is **lost**. Both operands are evaluated as function call arguments before the operator body runs.

```cpp
struct Bool {
    bool v;
    Bool operator&&(const Bool& rhs) const { return {v && rhs.v}; }
};

Bool a{false}, b = dangerous_operation();  // b is ALWAYS evaluated!
Bool result = a && b;  // no short-circuit — b computed before &&
```

This is why the C++ Core Guidelines recommend against overloading `&&` and `||`. Use explicit methods instead.

## Practical Checklist

- Use short-circuit `&&` for null/bounds guards before a potentially dangerous access.
- Use short-circuit `||` for fallback initialization or default values.
- Do not rely on the right side being evaluated — do not put necessary side effects there.
- Remember that overloading `&&`/`||` removes the short-circuit guarantee.
- `&` and `|` (bitwise) never short-circuit — do not use them as logical guards.

## Worked Example: Parsing a Config Line

```cpp
bool parse_line(const char* line, Config* out) {
    // Guard chain: each check protects the next
    return line != nullptr
        && line[0] != '#'           // skip comments
        && line[0] != '\n'          // skip blank lines
        && parse_key_value(line, out); // only called on valid lines
}
```

Each condition protects the next from invalid state. The right-to-left dependency is expressed naturally and safely.

**Interview answer:** "&&  and || short-circuit: the right operand is not evaluated if the result is already determined by the left. The left operand is fully sequenced before the right, making it safe for null-pointer guards and division-by-zero checks. Overloading these operators removes the short-circuit guarantee."
