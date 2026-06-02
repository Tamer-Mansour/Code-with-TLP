# Iterators and Lazy Evaluation

Rust's iterator system is one of its most elegant features. Iterators are **lazy**: they do no work until consumed. You chain adapters together and the compiler fuses them into a single tight loop — often matching hand-written C code in performance.

## The `Iterator` trait

Any type that implements `Iterator` provides a `next()` method that returns `Option<Item>`:

```rust
pub trait Iterator {
    type Item;
    fn next(&mut self) -> Option<Self::Item>;
    // + dozens of provided methods
}
```

Returning `None` signals exhaustion. You rarely call `next()` directly — you use the provided adapter methods.

## Creating iterators from collections

```rust
let v = vec![1, 2, 3];

v.iter()         // yields &i32 — borrows elements
v.iter_mut()     // yields &mut i32 — mutable borrows
v.into_iter()    // yields i32 — moves/consumes the Vec
```

Using `for` automatically calls `into_iter()`:

```rust
for x in vec![1, 2, 3] { /* x is i32 */ }
```

## Adapters — transform lazily

Adapters return a new iterator; nothing runs yet.

```rust
let v = vec![1, 2, 3, 4, 5];

// map — transform each element
let doubled: Vec<i32> = v.iter().map(|x| x * 2).collect();
// [2, 4, 6, 8, 10]

// filter — keep matching elements
let evens: Vec<&i32> = v.iter().filter(|x| *x % 2 == 0).collect();
// [2, 4]

// chain adapters together (still lazy)
let result: Vec<i32> = v.iter()
    .filter(|&&x| x > 2)
    .map(|&x| x * 10)
    .collect();
// [30, 40, 50]
```

## Consumers — trigger computation

Consumers call `next()` until `None`, producing a final value.

| Consumer          | Returns             | Purpose                            |
|-------------------|---------------------|------------------------------------|
| `collect()`       | Collection          | Gather into `Vec`, `HashMap`, etc. |
| `sum()`           | Numeric             | Sum all elements                   |
| `product()`       | Numeric             | Multiply all elements              |
| `count()`         | `usize`             | Count elements                     |
| `min()` / `max()` | `Option<T>`         | Smallest / largest                 |
| `any(|x| …)`     | `bool`              | True if any element matches        |
| `all(|x| …)`     | `bool`              | True if every element matches      |
| `find(|x| …)`    | `Option<&T>`        | First matching element             |
| `position(|x| …)` | `Option<usize>`    | Index of first match               |
| `fold(init, f)`  | Accumulator         | General reduction                  |
| `for_each(|x| …)`| `()`               | Side effects (like a `for` loop)   |

```rust
let sum: i32 = (1..=100).sum();             // 5050
let any_neg = vec![1, -2, 3].iter().any(|&x| x < 0);  // true
let total = vec![1, 2, 3].iter().fold(0, |acc, x| acc + x);  // 6
```

## `enumerate` and `zip`

```rust
let words = vec!["alpha", "beta", "gamma"];

for (i, w) in words.iter().enumerate() {
    println!("{}: {}", i, w);
}
// 0: alpha
// 1: beta
// 2: gamma

let a = vec![1, 2, 3];
let b = vec!["one", "two", "three"];
let pairs: Vec<_> = a.iter().zip(b.iter()).collect();
// [(1, "one"), (2, "two"), (3, "three")]
```

## `flat_map` and `flatten`

```rust
let words = vec!["hello world", "foo bar"];
let chars: Vec<&str> = words.iter()
    .flat_map(|s| s.split_whitespace())
    .collect();
// ["hello", "world", "foo", "bar"]
```

## Performance: zero-cost abstractions

The iterator chain:

```rust
let total: i32 = (0..1_000_000).filter(|x| x % 2 == 0).map(|x| x * x).sum();
```

compiles to a loop with no intermediate allocations — the compiler inlines and fuses each step. Benchmark it against the equivalent C loop and they're virtually identical.

## Writing your own iterator

```rust
struct Counter {
    count: u32,
    max: u32,
}

impl Iterator for Counter {
    type Item = u32;

    fn next(&mut self) -> Option<u32> {
        if self.count < self.max {
            self.count += 1;
            Some(self.count)
        } else {
            None
        }
    }
}

let c = Counter { count: 0, max: 5 };
let v: Vec<u32> = c.collect();   // [1, 2, 3, 4, 5]
```

Once you implement `next()`, you get all the adapter and consumer methods for free.
