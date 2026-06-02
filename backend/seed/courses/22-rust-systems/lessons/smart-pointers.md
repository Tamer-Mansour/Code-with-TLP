# Smart Pointers: Box, Rc, and RefCell

Rust's smart pointer types let you work with heap data, shared ownership, and interior mutability in a controlled way — without sacrificing memory safety.

## `Box<T>` — heap allocation

A `Box<T>` stores a value on the heap and automatically frees it when the box goes out of scope. Use it when:

- The type is too large to put on the stack.
- You need a recursive data type (a type that contains itself).
- You want to erase a concrete type behind a `dyn Trait` pointer.

```rust
let b = Box::new(42_i32);     // 42 is on the heap
println!("{}", *b);            // deref to get the value
// b is dropped here; heap memory is freed
```

### Recursive types need `Box`

```rust
enum List {
    Cons(i32, Box<List>),   // without Box, List would be infinite in size
    Nil,
}

let list = List::Cons(1, Box::new(List::Cons(2, Box::new(List::Nil))));
```

The box makes the recursive case a pointer (8 bytes), breaking the infinite size loop.

## `Rc<T>` — reference-counted shared ownership (single-threaded)

`Rc<T>` ("reference counted") lets multiple parts of your code share ownership of the same value. The value is freed when the reference count drops to zero.

```rust
use std::rc::Rc;

let a = Rc::new(String::from("shared data"));
let b = Rc::clone(&a);    // increments ref count; both a and b point to the same String
let c = Rc::clone(&a);

println!("ref count: {}", Rc::strong_count(&a));   // 3
// When a, b, c all go out of scope, the String is freed exactly once.
```

`Rc` is **not** `Send` — it is not thread-safe. For multi-threaded shared ownership, use `Arc<T>` (atomic reference counting, covered in the Concurrency lesson).

## `RefCell<T>` — interior mutability

Normally, if you have an `Rc<T>`, you can't mutate the `T` through any of the aliases — the borrow rules still apply. `RefCell<T>` moves the borrow checking from **compile time to runtime**, enabling mutation even through a shared reference.

```rust
use std::cell::RefCell;

let data = RefCell::new(vec![1, 2, 3]);

data.borrow().iter().for_each(|x| print!("{} ", x));  // immutable borrow
data.borrow_mut().push(4);                             // mutable borrow
println!("{:?}", data.borrow());   // [1, 2, 3, 4]
```

If two mutable borrows are active at the same time, `RefCell` panics at runtime. Use it only when you're sure the access pattern is correct but the compiler can't prove it.

## `Rc<RefCell<T>>` — shared mutable state (single-threaded)

This combination is idiomatic for single-threaded shared mutable data:

```rust
use std::rc::Rc;
use std::cell::RefCell;

let shared = Rc::new(RefCell::new(0_i32));

let clone1 = Rc::clone(&shared);
let clone2 = Rc::clone(&shared);

*clone1.borrow_mut() += 10;
*clone2.borrow_mut() += 20;

println!("{}", shared.borrow());   // 30
```

For multi-threaded equivalent: `Arc<Mutex<T>>`.

## Comparison table

| Smart pointer    | Ownership       | Mutability        | Thread-safe? |
|------------------|-----------------|-------------------|--------------|
| `Box<T>`         | Single owner    | Normal rules      | Yes          |
| `Rc<T>`          | Multiple owners | Immutable by default | No        |
| `Arc<T>`         | Multiple owners | Immutable by default | Yes       |
| `RefCell<T>`     | Single owner    | Runtime-checked   | No           |
| `Mutex<T>`       | Single owner    | Runtime-checked (locked) | Yes   |
| `Rc<RefCell<T>>` | Multiple owners | Runtime-checked   | No           |
| `Arc<Mutex<T>>` | Multiple owners | Runtime-checked (locked) | Yes  |

## `Deref` and `Drop`

Smart pointers work because they implement two key traits:

- **`Deref`** — lets `*box_val` give you `T`; enables deref coercions (e.g., `Box<String>` → `&str`).
- **`Drop`** — called automatically when the smart pointer goes out of scope; frees resources (RAII).

You can implement these traits on your own types to create custom smart pointers.

```rust
struct MyBox<T>(T);

impl<T> std::ops::Deref for MyBox<T> {
    type Target = T;
    fn deref(&self) -> &T { &self.0 }
}
```
