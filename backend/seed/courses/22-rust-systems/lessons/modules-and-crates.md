# Modules and Crates

As your Rust projects grow beyond a single file, you need the module system to organize code, control visibility, and split work across files.

## Crates and packages

| Term        | Meaning                                                        |
|-------------|----------------------------------------------------------------|
| **crate**   | The smallest compilation unit — a binary or a library          |
| **package** | One or more crates sharing a `Cargo.toml`                      |
| **workspace**| Multiple packages sharing one `Cargo.lock` and `target/`     |

`cargo new my-app` creates a binary crate with `src/main.rs` as the root.
`cargo new my-lib --lib` creates a library crate with `src/lib.rs` as the root.

A package can have at most one library crate and any number of binary crates (in `src/bin/`).

## Declaring modules inline

```rust
// src/main.rs
mod math {
    pub fn add(a: i32, b: i32) -> i32 {
        a + b
    }

    // Private by default — not accessible outside the module
    fn helper() -> i32 { 0 }
}

fn main() {
    println!("{}", math::add(2, 3));   // 5
}
```

`pub` makes an item visible outside the module. Everything is private by default.

## Splitting into files

Move a module to its own file by matching the module name:

```
src/
  main.rs
  math.rs       ← or  math/mod.rs  (older style)
```

```rust
// src/math.rs
pub fn add(a: i32, b: i32) -> i32 { a + b }
```

```rust
// src/main.rs
mod math;   // tells the compiler to look for src/math.rs

fn main() {
    println!("{}", math::add(2, 3));
}
```

For nested modules:

```
src/
  main.rs
  shapes/
    mod.rs      ← declares submodules; also src/shapes.rs works in Rust 2018+
    circle.rs
    rect.rs
```

## The `use` keyword

Bring paths into scope to avoid repeating long prefixes:

```rust
use std::collections::HashMap;
use std::io::{self, Write};   // both io and io::Write

let mut m: HashMap<&str, i32> = HashMap::new();
io::stdout().flush().unwrap();
```

### Aliasing

```rust
use std::fmt::Result as FmtResult;
use std::io::Result as IoResult;
```

### Re-exporting with `pub use`

```rust
// src/lib.rs
mod shapes;
pub use shapes::circle::Circle;   // callers can do `my_lib::Circle` directly
```

## Visibility modifiers

| Modifier         | Visible to…                              |
|------------------|------------------------------------------|
| (none)           | Only the current module                  |
| `pub`            | Anywhere                                 |
| `pub(crate)`     | Anywhere inside this crate               |
| `pub(super)`     | Parent module only                       |
| `pub(in path)`   | The named ancestor module                |

```rust
pub(crate) fn internal_only() {}  // visible within this crate, not to library users
```

## Adding external dependencies

```toml
# Cargo.toml
[dependencies]
serde = { version = "1", features = ["derive"] }
rand = "0.8"
```

```bash
cargo add serde --features derive   # shortcut; updates Cargo.toml automatically
```

Then use in code:

```rust
use serde::{Serialize, Deserialize};
use rand::Rng;
```

`crates.io` is the central registry — `cargo search <keyword>` lists available crates.

## Workspaces

For a multi-crate project:

```toml
# Cargo.toml at the root
[workspace]
members = [
    "core",
    "server",
    "cli",
]
```

All members share `target/` and `Cargo.lock`. Build everything with `cargo build` at the root.

## Best practices

- Keep the public API surface minimal — only `pub` what callers genuinely need.
- Group related types and functions in the same module, not just because they share a filename.
- Use `pub(crate)` liberally for internal helpers that multiple modules share but you don't want to expose.
- Prefer `use crate::…` (absolute from crate root) over `use super::…` chains for clarity.
