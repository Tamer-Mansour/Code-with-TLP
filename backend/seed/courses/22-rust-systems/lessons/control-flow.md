# Control Flow in Rust

Rust has the standard control-flow tools — `if`, `loop`, `while`, `for` — with a few twists that make them more expressive than their equivalents in C or Python.

## `if` as an expression

In Rust, `if` is an **expression**: it produces a value.

```rust
let number = 7;
let description = if number % 2 == 0 { "even" } else { "odd" };
println!("{} is {}", number, description);
```

Both branches must produce the same type. The compiler rejects mismatched types.

## Pattern matching with `match`

`match` is Rust's most powerful control-flow construct. It works like a `switch` on steroids — exhaustive, pattern-based, and itself an expression.

```rust
let coin = 25_u32;

let name = match coin {
    1  => "penny",
    5  => "nickel",
    10 => "dime",
    25 => "quarter",
    _  => "unknown",   // catch-all
};
println!("{}", name);  // quarter
```

The `_` arm matches everything not handled above. The compiler **forces** you to handle all cases (exhaustiveness check).

### Matching ranges and guards

```rust
let score = 82;

let grade = match score {
    90..=100 => "A",
    80..=89  => "B",
    70..=79  => "C",
    _        => "F",
};
```

### Destructuring in match arms

```rust
let point = (3, -2);

match point {
    (0, 0) => println!("origin"),
    (x, 0) => println!("on x-axis at {}", x),
    (0, y) => println!("on y-axis at {}", y),
    (x, y) => println!("({}, {})", x, y),
}
```

## Loops

### `loop` — infinite loop with `break` return value

```rust
let mut counter = 0;
let result = loop {
    counter += 1;
    if counter == 10 {
        break counter * 2;   // returns 20 from the loop expression
    }
};
println!("{}", result);   // 20
```

### `while`

```rust
let mut n = 3;
while n > 0 {
    println!("{}", n);
    n -= 1;
}
println!("liftoff!");
```

### `for` over iterators — the idiomatic choice

```rust
let a = [10, 20, 30, 40, 50];
for x in a {
    println!("{}", x);
}
```

Use a range for a numeric count:

```rust
for i in 0..5 {        // 0, 1, 2, 3, 4
    print!("{} ", i);
}

for i in (0..5).rev() {   // 4, 3, 2, 1, 0
    print!("{} ", i);
}
```

## `if let` — ergonomic single-variant matching

When you only care about one branch of a `match`, `if let` is cleaner:

```rust
let some_value: Option<i32> = Some(42);

if let Some(v) = some_value {
    println!("got {}", v);
}
// No else needed; non-Some values are silently skipped
```

## `while let`

Useful for draining an iterator or stack:

```rust
let mut stack = vec![1, 2, 3];
while let Some(top) = stack.pop() {
    println!("{}", top);   // 3, 2, 1
}
```

## Summary

| Construct  | Use when…                                         |
|------------|---------------------------------------------------|
| `if`/`else`| Simple condition; also useful as an expression     |
| `match`    | Multiple patterns, enum variants, exhaustiveness   |
| `loop`     | Infinite loops or retry-until-done with a return value |
| `while`    | Condition checked before each iteration            |
| `for`      | Iterating over a collection or range (idiomatic)   |
| `if let`   | Handling one variant without a full `match`        |

Prefer `for` over `while` for iteration — it can't go out of bounds and conveys intent more clearly.
