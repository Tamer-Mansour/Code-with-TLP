# Structs and Enums

## Structs

```rust
struct User {
    id: u64,
    name: String,
    email: String,
}

let u = User {
    id: 1,
    name: String::from("Alice"),
    email: String::from("a@x.com"),
};

println!("{}", u.name);
```

Shorthand when field names match local variables:

```rust
fn new_user(id: u64, name: String, email: String) -> User {
    User { id, name, email }      // same as id: id, name: name, ...
}
```

Update syntax:

```rust
let u2 = User { email: String::from("new@x.com"), ..u };
```

## Tuple structs

```rust
struct Point(f64, f64);
let p = Point(1.0, 2.0);
println!("{} {}", p.0, p.1);
```

Useful for strong typing: `struct UserId(u64)`, `struct Meters(f64)` — same as `u64` / `f64` underneath but the compiler enforces you don't mix them up.

## Unit struct

```rust
struct UnitMarker;     // zero-sized
```

For traits that need no data.

## Methods with impl

```rust
impl User {
    fn new(name: &str, email: &str) -> Self {
        Self {
            id: next_id(),
            name: name.to_string(),
            email: email.to_string(),
        }
    }

    fn greet(&self) -> String {
        format!("Hi, {}", self.name)
    }

    fn rename(&mut self, name: &str) {
        self.name = name.to_string();
    }
}
```

- `&self` — immutable borrow.
- `&mut self` — mutable borrow.
- `self` — moves the value (consumed).

Associated functions (no receiver) — called like `User::new("Alice", "a@x.com")`.

## Enums

Enums in Rust are tagged unions — each variant can carry data of any shape:

```rust
enum Shape {
    Circle(f64),                  // radius
    Square(f64),                  // side
    Rectangle { w: f64, h: f64 }, // named fields
}

let s = Shape::Circle(2.5);
```

## Pattern matching

```rust
fn area(s: &Shape) -> f64 {
    match s {
        Shape::Circle(r) => std::f64::consts::PI * r * r,
        Shape::Square(side) => side * side,
        Shape::Rectangle { w, h } => w * h,
    }
}
```

The compiler verifies you handled every variant. Add a new variant later → compiler error at every `match`.

## Option<T> and Result<T, E>

The most-used enums in Rust:

```rust
enum Option<T> { Some(T), None }
enum Result<T, E> { Ok(T), Err(E) }
```

```rust
let x: Option<i32> = Some(5);
match x {
    Some(n) => println!("got {}", n),
    None => println!("nothing"),
}
```

We cover them in detail in the Result/Option lesson.

## if let, while let

Match a single pattern without writing a full `match`:

```rust
if let Some(n) = some_value {
    println!("{}", n);
}

while let Some(x) = iter.next() {
    process(x);
}
```

## Derive macros

```rust
#[derive(Debug, Clone, PartialEq, Eq, Hash)]
struct User {
    id: u64,
    name: String,
}

println!("{:?}", u);   // Debug formatting
let u2 = u.clone();
```

Common derives: `Debug` (for `{:?}` printing), `Clone`, `Copy` (for cheap value types), `PartialEq`/`Eq`, `Hash`, `Default`, `serde::Serialize`/`Deserialize`.
