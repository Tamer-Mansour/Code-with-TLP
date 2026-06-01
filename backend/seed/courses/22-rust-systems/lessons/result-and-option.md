# Result, Option, and ?

Rust has no `null`, no exceptions. Two enums replace both: `Option<T>` for absence, `Result<T, E>` for fallible operations.

## Option<T>

```rust
fn find(name: &str) -> Option<User> {
    if exists(name) { Some(User { ... }) } else { None }
}

match find("Alice") {
    Some(u) => println!("found {}", u.name),
    None => println!("not found"),
}
```

Common methods:

```rust
let x: Option<i32> = Some(5);

x.is_some();              // true
x.is_none();              // false
x.unwrap();               // 5, panics if None
x.unwrap_or(0);           // value or default
x.unwrap_or_else(|| compute_default());
x.unwrap_or_default();    // requires Default

x.map(|n| n * 2);         // Option<i32> -> Option<i32>
x.and_then(|n| if n > 0 { Some(n) } else { None });   // flat_map
x.ok_or("missing");       // Option<T> -> Result<T, E>
```

## Result<T, E>

```rust
fn parse_age(s: &str) -> Result<u32, String> {
    s.parse::<u32>().map_err(|e| format!("can't parse {}: {}", s, e))
}

match parse_age("30") {
    Ok(n) => println!("age is {}", n),
    Err(e) => eprintln!("{}", e),
}
```

Methods mirror `Option`:

```rust
let r: Result<i32, &str> = Ok(5);

r.is_ok(); r.is_err();
r.unwrap();
r.unwrap_or(0);
r.expect("must be a positive number");

r.map(|n| n * 2);
r.map_err(|e| format!("error: {}", e));
r.and_then(|n| if n > 0 { Ok(n) } else { Err("negative") });
r.ok();      // Result<T, E> -> Option<T>
```

## The ? operator — error propagation

```rust
fn read_user_age(path: &str) -> Result<u32, Box<dyn std::error::Error>> {
    let body = std::fs::read_to_string(path)?;    // returns early if Err
    let parsed: serde_json::Value = serde_json::from_str(&body)?;
    let age = parsed["age"].as_u64().ok_or("missing age")?;
    Ok(age as u32)
}
```

`?` does:

1. If `Ok(value)` → unwrap to `value` and continue.
2. If `Err(e)` → return `Err(e.into())` immediately, converting via `From` if needed.

It only works inside functions returning `Result` (or `Option`).

## Custom error types

```rust
#[derive(Debug)]
enum AppError {
    NotFound,
    Invalid(String),
    Io(std::io::Error),
}

impl std::fmt::Display for AppError {
    fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        match self {
            AppError::NotFound => write!(f, "not found"),
            AppError::Invalid(s) => write!(f, "invalid: {}", s),
            AppError::Io(e) => write!(f, "io: {}", e),
        }
    }
}

impl std::error::Error for AppError {}

impl From<std::io::Error> for AppError {
    fn from(e: std::io::Error) -> Self { AppError::Io(e) }
}
```

With `From`, the `?` operator auto-converts `io::Error` into `AppError`.

## anyhow and thiserror

In real code, use:

- **`thiserror`** — derive macros for `Display`/`From` on custom error enums.
- **`anyhow`** — `anyhow::Result<T>` for application code where you don't care about specific error types.

```rust
use anyhow::{Context, Result};

fn run() -> Result<()> {
    let body = std::fs::read_to_string("config.toml")
        .context("reading config.toml")?;
    parse(&body).context("parsing config")?;
    Ok(())
}
```

## Don't unwrap in libraries

`unwrap()` panics. Fine in throwaway scripts and tests. **In library code, propagate with `?`** so callers can decide how to handle errors.
