# Traits and Generics

## Traits — shared behavior

A **trait** declares a set of methods a type can implement. Like interfaces in other languages, but more powerful — they support default methods, generics, and associated types.

```rust
trait Greet {
    fn greet(&self) -> String;

    fn loud(&self) -> String {     // default implementation
        self.greet().to_uppercase()
    }
}

struct Dog;
impl Greet for Dog {
    fn greet(&self) -> String { "woof".into() }
}

let d = Dog;
println!("{}", d.greet());     // "woof"
println!("{}", d.loud());      // "WOOF"
```

## Generic functions

```rust
fn largest<T: PartialOrd>(items: &[T]) -> &T {
    let mut max = &items[0];
    for x in &items[1..] {
        if x > max { max = x; }
    }
    max
}
```

`T: PartialOrd` is a **trait bound** — T must implement `PartialOrd` (the `<`, `>` operators).

Multiple bounds:

```rust
fn print<T: std::fmt::Debug + Clone>(x: T) {
    let y = x.clone();
    println!("{:?}", y);
}
```

Or with `where`:

```rust
fn print<T>(x: T) where T: Debug + Clone {
    ...
}
```

## Implementing traits for your types

```rust
use std::fmt;

impl fmt::Display for User {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        write!(f, "User({}, {})", self.id, self.name)
    }
}

println!("{}", u);
```

## Generic structs

```rust
struct Container<T> {
    items: Vec<T>,
}

impl<T: Clone> Container<T> {
    fn first(&self) -> Option<T> {
        self.items.first().cloned()
    }
}
```

The `impl<T: Clone>` syntax adds the bound only where it's needed.

## Trait objects (dynamic dispatch)

```rust
fn print_all(items: &[Box<dyn Greet>]) {
    for item in items {
        println!("{}", item.greet());
    }
}
```

`dyn Greet` is a **trait object** — a fat pointer at runtime, vtable lookup per call. Use when you need a heterogeneous collection of types implementing the same trait.

Static dispatch via generics is faster (monomorphized at compile time). Use generics by default; reach for `dyn` when you need runtime polymorphism.

## Common standard library traits

| Trait                | What it provides                                |
|----------------------|-------------------------------------------------|
| `Clone`              | `.clone()` deep copy                            |
| `Copy`               | implicit copy (memcpy)                          |
| `Debug`              | `{:?}` formatting                               |
| `Display`            | `{}` formatting                                 |
| `Default`            | `Type::default()` zero/empty value              |
| `PartialEq`, `Eq`    | equality                                        |
| `PartialOrd`, `Ord`  | comparison                                      |
| `Hash`               | hashable                                        |
| `Iterator`           | `for x in ...`                                  |
| `From<T>` / `Into<T>`| conversions                                     |
| `AsRef<T>` / `AsMut<T>` | cheap reference-like conversions             |
| `Drop`               | run code when value is dropped                  |

## Iterator — the killer trait

```rust
let nums: Vec<i32> = (1..=10).collect();
let sum_squares: i32 = nums.iter()
    .filter(|&&n| n % 2 == 0)
    .map(|&n| n * n)
    .sum();
```

`Iterator` has dozens of adapter methods: `map`, `filter`, `take`, `skip`, `chain`, `zip`, `enumerate`, `fold`, `scan`, `step_by`, `rev`, etc. All lazy; nothing happens until a consumer (`collect`, `sum`, `for`) drives it.

Implementing your own iterator means a single `next()` method:

```rust
struct Counter(u32);
impl Iterator for Counter {
    type Item = u32;
    fn next(&mut self) -> Option<u32> {
        self.0 += 1;
        if self.0 <= 10 { Some(self.0) } else { None }
    }
}
```

All the adapter methods come free.
