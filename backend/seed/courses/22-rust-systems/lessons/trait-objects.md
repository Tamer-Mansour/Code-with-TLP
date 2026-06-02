# Trait Objects and Dynamic Dispatch

Generics give you **static dispatch** — the compiler generates a separate function for each concrete type. Sometimes you need **dynamic dispatch** — a pointer to any type that implements a trait, decided at runtime. That's where trait objects come in.

## `dyn Trait` — runtime polymorphism

A trait object is written as `&dyn Trait` or `Box<dyn Trait>`. The compiler inserts a **vtable** (a table of function pointers) and resolves method calls at runtime.

```rust
trait Animal {
    fn speak(&self) -> &str;
}

struct Dog;
struct Cat;

impl Animal for Dog { fn speak(&self) -> &str { "woof" } }
impl Animal for Cat { fn speak(&self) -> &str { "meow" } }

fn make_sound(animal: &dyn Animal) {
    println!("{}", animal.speak());
}

let dog = Dog;
let cat = Cat;
make_sound(&dog);   // "woof"
make_sound(&cat);   // "meow"
```

## Storing mixed types in a `Vec`

The most common use case: a heterogeneous collection of objects that share a trait.

```rust
let mut animals: Vec<Box<dyn Animal>> = Vec::new();
animals.push(Box::new(Dog));
animals.push(Box::new(Cat));
animals.push(Box::new(Dog));

for a in &animals {
    println!("{}", a.speak());
}
```

With generics this would be impossible — `Vec<Dog>` can only hold `Dog`s. With `Box<dyn Animal>` you can mix any types that implement `Animal`.

## Object safety rules

Not every trait can be made into a trait object. A trait is **object-safe** when:

1. It has no methods that are generic (have type parameters) on the method itself.
2. It has no methods that return `Self`.
3. It has no associated functions without a `self` receiver (unless `where Self: Sized`).

```rust
trait Cloneable: Clone {}   // NOT object-safe: Clone returns Self
trait Printable {
    fn print(&self);         // object-safe: takes &self, no generics
}
```

## Static vs dynamic dispatch — when to use which

| Criterion                     | Generics (`impl Trait` / `T: Trait`) | Trait objects (`dyn Trait`)  |
|-------------------------------|--------------------------------------|------------------------------|
| Performance                   | Faster (inlined, monomorphized)       | Slight overhead (vtable lookup) |
| Binary size                   | Grows (one copy per type)             | Single copy                  |
| Heterogeneous collections     | Not possible                         | Yes                          |
| Known types at compile time   | Yes                                  | No                           |
| Recursive / plugin systems    | Awkward                              | Natural                      |

## `impl Trait` in function positions

A lighter alternative to trait objects when you just want to express "some type implementing this trait":

```rust
// In parameter position — static dispatch, caller chooses the type
fn print_area(shape: &impl Shape) { … }

// In return position — static dispatch, one concrete type returned
fn make_circle() -> impl Shape { Circle { radius: 1.0 } }
```

`impl Trait` in return position works only when you always return the same concrete type. If different code paths return different types, you must use `Box<dyn Trait>`.

## Combining trait objects with error handling

```rust
use std::fmt;

trait Greet: fmt::Display {
    fn greet(&self) -> String;
}

fn greet_all(greeters: &[Box<dyn Greet>]) {
    for g in greeters {
        println!("{}", g.greet());
    }
}
```

This pattern is used extensively in Rust's error ecosystem — `Box<dyn std::error::Error>` is the universal return type for functions that might fail in different ways.

## Example: plugin-style architecture

```rust
trait Plugin {
    fn name(&self) -> &str;
    fn run(&self, input: &str) -> String;
}

struct Plugins {
    list: Vec<Box<dyn Plugin>>,
}

impl Plugins {
    fn register(&mut self, p: Box<dyn Plugin>) {
        self.list.push(p);
    }

    fn run_all(&self, input: &str) {
        for p in &self.list {
            println!("[{}] {}", p.name(), p.run(input));
        }
    }
}
```

The calling code doesn't know what concrete `Plugin` types exist — they're injected at runtime. This is the same pattern used in test frameworks, plugin systems, and UI frameworks.
