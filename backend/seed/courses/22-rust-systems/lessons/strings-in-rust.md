# Strings in Rust: `String` vs `&str`

Rust has two string types, and understanding the difference prevents a whole class of borrow-checker fights.

## `&str` — string slice (borrowed)

A `&str` is a **reference to a UTF-8 byte sequence** stored somewhere else — usually a string literal baked into the binary, or a slice of a `String`.

```rust
let greeting: &str = "hello";          // string literal — lives forever
let word: &str = &"hello world"[0..5]; // slice of a longer string
```

`&str` is unsized; you always use it behind a reference. It is `Copy`.

## `String` — owned, growable string

A `String` is a heap-allocated, mutable, growable UTF-8 string. Use it when you need to build or modify a string at runtime.

```rust
let mut s = String::from("hello");
s.push(' ');                    // append a char
s.push_str("world");            // append a &str
s += "!";                       // also works via Add trait
println!("{}", s);              // "hello world!"
```

## Conversion

```rust
let owned: String = "hello".to_string();
let owned: String = String::from("hello");

let borrowed: &str = &owned;            // deref coercion
let borrowed: &str = owned.as_str();   // explicit
```

## When to use which

| Scenario                                      | Type to use  |
|-----------------------------------------------|--------------|
| Function parameter — read-only                | `&str`       |
| Return value you create at runtime            | `String`     |
| Storing a string field in a struct            | `String`     |
| String literal, config constant               | `&str`       |
| Building up a string in a loop                | `String`     |

Prefer `&str` in function signatures — a caller can pass both `&str` and `&String` (via deref coercion), making your API more flexible.

## Common string operations

```rust
let s = String::from("  hello world  ");

s.trim()                       // "&str" without leading/trailing whitespace
s.to_uppercase()               // new String
s.contains("world")            // bool
s.starts_with("  he")          // bool
s.replace("world", "Rust")     // new String
s.split_whitespace()           // iterator of &str tokens
s.lines()                      // iterator over lines
```

### Splitting and collecting

```rust
let csv = "1,2,3,4,5";
let nums: Vec<i32> = csv.split(',')
    .map(|s| s.parse().unwrap())
    .collect();
// [1, 2, 3, 4, 5]
```

### Building with `format!`

```rust
let first = "Ada";
let last  = "Lovelace";
let full  = format!("{} {}", first, last);  // "Ada Lovelace"
```

`format!` returns a `String` without printing it — handy for constructing messages.

## UTF-8 and indexing

Rust strings are always valid UTF-8. Indexing by byte position is possible but must be done carefully because a Unicode scalar value can be 1–4 bytes:

```rust
let s = "café";
// s[0..3] is "caf" — OK, the first 3 chars happen to be 1 byte each
// s[0..4] is NOT "café" — 'é' is 2 bytes (U+00E9 = 0xC3 0xA9)

// Safe: iterate over chars
for c in "café".chars() {
    print!("{} ", c);   // c a f é
}
```

Avoid `s[i]` for character access; use `chars().nth(i)` or a byte-level slice only when you control the encoding.

## `String` vs `&str` in structs

```rust
// Owned — the struct can outlive wherever the data came from
struct Config {
    host: String,
    port: u16,
}

// Borrowed — requires a lifetime annotation (advanced)
struct View<'a> {
    content: &'a str,
}
```

For most structs, store `String`. Use `&str` with lifetime annotations when you know the data is always borrowed from a longer-lived buffer and want to avoid cloning.
