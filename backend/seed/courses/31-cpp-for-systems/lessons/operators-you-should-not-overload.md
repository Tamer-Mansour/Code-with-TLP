# Operators You Should Not Overload

Not every operator that *can* be overloaded *should* be. Some operators have built-in semantics that code throughout the ecosystem relies on. Overloading them breaks those assumptions and produces silent, hard-to-debug bugs.

## Operators You Cannot Overload At All

The language forbids overloading these:

| Operator | Name |
|----------|------|
| `::` | Scope resolution |
| `.` | Member access |
| `.*` | Pointer-to-member access |
| `?:` | Ternary / conditional |
| `sizeof` | Size query |
| `typeid` | Type query |
| `alignof` | Alignment query |

## Operators You Technically Can, But Should Not

### `&&` and `||` (Logical AND/OR)

The built-in versions **short-circuit**: the right operand is not evaluated if the left already determines the result.

```cpp
if (ptr != nullptr && ptr->isValid()) { ... }
// If ptr == nullptr, ptr->isValid() is never called
```

An overloaded `&&` is a regular function call — **both arguments are evaluated before the call**. The short-circuit guarantee is gone:

```cpp
struct Expr {
    bool val;
    Expr operator&&(const Expr& rhs) const { return {val && rhs.val}; }
    // rhs is ALREADY evaluated before this is called — no short-circuit!
};
```

Anyone reading `a && b` expects short-circuit semantics. Violating that is a trap.

### `,` (Comma Operator)

The built-in comma operator evaluates the left, discards it, then evaluates and returns the right. Overloading it changes this:

```cpp
// All valid C++, all terrible:
Expr operator,(const Expr& lhs, const Expr& rhs);
```

Real code occasionally relies on the comma's sequencing guarantee. Overloading it creates subtle misbehaviours in template code and macros.

### `&` (Unary Address-Of)

Taking the address of an object should always give a pointer to that object. Overloading `&` can break generic code that captures addresses:

```cpp
// Breaks std::addressof, placement new patterns, and library internals
MyType* operator&() { return some_other_pointer; }
```

If you need a "smart address", use a named function. The standard library provides `std::addressof()` specifically to bypass overloaded `&`.

### `new` and `delete`

These *can* be overloaded for custom allocators and are occasionally legitimate. But casual overloading introduces memory safety hazards:

- Every `new` must be matched by the correct `delete`.
- Mixing overloaded and global allocators in the same program is a source of subtle corruption.

Use them only when building a custom allocator, arena, or pool, and document the contract clearly.

## The `->*` Operator

Overloading the pointer-to-member-dereference operator is technically possible but extremely rarely correct. It confuses readers and has no common legitimate use case outside of proxy types that emulate raw pointers.

## The Principle

> **Only overload an operator if your type truly *is* that mathematical or semantic concept.**

If your class is not a number, do not overload `+`. If it is not a smart pointer, do not overload `->`. If you feel tempted to use `<<` for "bit-shift a configuration object left", choose a named method instead.

## Summary Table

| Operator | Overloadable? | Should you? |
|----------|--------------|-------------|
| `&&`, `\|\|` | Yes | No — breaks short-circuit |
| `,` | Yes | No — breaks sequencing |
| `&` (unary) | Yes | No — breaks `std::addressof` |
| `new`/`delete` | Yes | Only for custom allocators |
| `->*` | Yes | Almost never |
| `::`, `.`, `.*`, `?:` | No | — |

## Named Alternatives

When an operator would be misleading, use a method:

```cpp
// BAD: repurposing + for "append"
myList = myList + item;

// GOOD: clear intent
myList.append(item);
myList.push_back(item);
```

> **Interview answer:** `&&` and `||` should never be overloaded because their built-in short-circuit evaluation disappears when they become function calls — both operands are always evaluated. The comma operator and unary `&` should similarly be avoided as their overloads break generic code that depends on built-in sequencing and address-taking semantics.
