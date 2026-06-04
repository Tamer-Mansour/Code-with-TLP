# constexpr Fibonacci Evaluator

Simulate C++ `constexpr` evaluation context rules for a Fibonacci function.

## Fibonacci Definition

`fib(0) = 0`, `fib(1) = 1`, `fib(n) = fib(n-1) + fib(n-2)` for `n >= 2`.

## Operations

- `CONSTEXPR_CONTEXT n` — evaluate `fib(n)` in a compile-time context
  - Print: `COMPILE-TIME: fib(n)=K`
- `RUNTIME_CONTEXT n` — evaluate `fib(n)` in a runtime context
  - Print: `RUNTIME: fib(n)=K`
- `IS_CONSTEXPR n` — can `fib(n)` be a constant expression given `n` is an integer literal?
  - Print: `YES` if `n >= 0`, otherwise `NO`

## Input Format

- Line 1: integer `M`
- Lines 2..M+1: one operation per line

## Output Format

One line per operation.

## Example

**Input:**
```
5
CONSTEXPR_CONTEXT 10
RUNTIME_CONTEXT 10
IS_CONSTEXPR 15
CONSTEXPR_CONTEXT 0
RUNTIME_CONTEXT 7
```

**Output:**
```
COMPILE-TIME: fib(10)=55
RUNTIME: fib(10)=55
YES
COMPILE-TIME: fib(0)=0
RUNTIME: fib(7)=13
```

## Constraints

- `1 <= M <= 50`
- `0 <= n <= 35` for CONSTEXPR_CONTEXT and RUNTIME_CONTEXT
- `n` may be any integer for IS_CONSTEXPR (answer YES only if `n >= 0`)
