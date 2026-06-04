# Variable Scope Simulator

Practice identifying the output of JavaScript variable declarations across different scoping contexts.

This exercise tests your understanding of:
- `var` function scope and hoisting
- `let` block scope and the Temporal Dead Zone
- The classic `var`-in-loop closure bug

## Background

One of the most common JavaScript bugs involves using `var` inside a `for` loop with asynchronous callbacks. Because `var` is function-scoped (not block-scoped), all iterations share the **same** variable. When callbacks fire later, they all see the variable's **final** value.

```javascript
// Classic bug with var
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0);
}
// Prints: 3, 3, 3   (NOT 0, 1, 2)
```

Using `let` creates a **new binding per iteration**, so each closure captures its own copy:

```javascript
// Fixed with let
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0);
}
// Prints: 0, 1, 2
```

## Task

Given T test cases, each describing a variable declaration and context, output what JavaScript would produce.

## Input Format

```
T
keyword varname value context
...
```

- `keyword`: `var` or `let`
- `varname`: a valid identifier (ignored for output, shown for context)
- `value`: a positive integer N
- `context`: `loop` or `function`

## Output Rules

- **loop + var**: print `loop: ` followed by `value` repeated `value` times, space-separated (all closures capture the final value)
- **loop + let**: print `loop: ` followed by `0 1 2 ... value-1` space-separated (each closure gets its own binding)
- **function (any keyword)**: print `function: value`

## Examples

**Input:**
```
3
var counter 3 loop
let counter 3 loop
var x 42 function
```

**Output:**
```
loop: 3 3 3
loop: 0 1 2
function: 42
```

## Constraints

- 1 ≤ T ≤ 100
- 1 ≤ value ≤ 20
