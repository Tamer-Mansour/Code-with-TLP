# Collections: Vec, HashMap, and HashSet

Rust's standard library provides three workhorse collection types you'll reach for constantly: `Vec<T>`, `HashMap<K, V>`, and `HashSet<T>`. All three live in `std::collections`.

## `Vec<T>` — growable array

A `Vec` stores elements of one type contiguously in heap memory. It grows automatically.

```rust
let mut v: Vec<i32> = Vec::new();
v.push(1);
v.push(2);
v.push(3);

// Shorthand with the vec! macro
let v = vec![1, 2, 3, 4, 5];

println!("{}", v[2]);          // 3 — panics on out-of-bounds
println!("{:?}", v.get(10));   // None — safe access
```

### Common Vec operations

| Method            | What it does                                |
|-------------------|---------------------------------------------|
| `push(x)`         | Append to the end                           |
| `pop()`           | Remove and return the last element (`Option`) |
| `len()`           | Number of elements                          |
| `is_empty()`      | True if len == 0                            |
| `contains(&x)`    | Linear search                               |
| `sort()`          | In-place sort (requires `Ord`)              |
| `dedup()`         | Remove consecutive duplicates               |
| `retain(|x| …)`  | Keep only elements matching a predicate     |
| `extend(iter)`    | Append from any iterator                    |

### Iterating

```rust
let v = vec![10, 20, 30];

// Immutable references — borrow v
for x in &v {
    println!("{}", x);
}

// Mutable references — modify in place
let mut v = vec![1, 2, 3];
for x in &mut v {
    *x *= 2;
}
// v is now [2, 4, 6]

// Consuming — takes ownership of each element
for x in v {
    println!("{}", x);
}
// v is gone (moved)
```

## `HashMap<K, V>` — hash table

Requires both keys and values to be owned (or bounded by lifetime). Keys must implement `Eq + Hash`.

```rust
use std::collections::HashMap;

let mut scores: HashMap<String, i32> = HashMap::new();
scores.insert("Alice".to_string(), 95);
scores.insert("Bob".to_string(), 87);

// Access
println!("{:?}", scores.get("Alice"));    // Some(95)
println!("{}", scores["Alice"]);           // 95 — panics if missing

// Conditional insert (very common pattern)
scores.entry("Carol".to_string()).or_insert(70);

// Iteration
for (name, score) in &scores {
    println!("{}: {}", name, score);
}
```

### Updating values

```rust
let text = "hello world hello rust hello";
let mut freq: HashMap<&str, u32> = HashMap::new();

for word in text.split_whitespace() {
    let count = freq.entry(word).or_insert(0);
    *count += 1;
}
// freq = {"hello": 3, "world": 1, "rust": 1}
```

`entry().or_insert()` returns a mutable reference to the value — a pattern you'll write constantly.

## `HashSet<T>` — unique values

```rust
use std::collections::HashSet;

let mut set: HashSet<i32> = HashSet::new();
set.insert(1);
set.insert(2);
set.insert(2);   // duplicate — ignored
set.insert(3);

println!("{}", set.len());           // 3
println!("{}", set.contains(&2));   // true

// Set operations
let a: HashSet<i32> = [1, 2, 3].iter().cloned().collect();
let b: HashSet<i32> = [2, 3, 4].iter().cloned().collect();

let intersection: HashSet<_> = a.intersection(&b).collect();  // {2, 3}
let union: HashSet<_>        = a.union(&b).collect();          // {1, 2, 3, 4}
let diff: HashSet<_>         = a.difference(&b).collect();     // {1}
```

## Choosing the right collection

| Situation                              | Use              |
|----------------------------------------|------------------|
| Ordered sequence, fast append/pop-end | `Vec<T>`         |
| Key→value lookup                       | `HashMap<K, V>`  |
| Membership / deduplication             | `HashSet<T>`     |
| FIFO queue                             | `VecDeque<T>`    |
| Ordered map (sorted by key)            | `BTreeMap<K, V>` |

For most use cases `Vec` and `HashMap` are sufficient. Reach for `BTreeMap` when you need deterministic iteration order.
