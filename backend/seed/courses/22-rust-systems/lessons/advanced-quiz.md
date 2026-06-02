# Quiz: Advanced Rust Concepts

**Q1. What is the main difference between `Rc<T>` and `Arc<T>`?**
- [ ] `Rc<T>` is heap-allocated; `Arc<T>` is stack-allocated.
- [x] `Arc<T>` uses atomic operations for its reference count, making it safe to share across threads; `Rc<T>` is not thread-safe.
- [ ] `Arc<T>` allows mutable access; `Rc<T>` does not.
- [ ] They are identical; `Arc` is just an alias for `Rc`.

**Q2. When would you choose `Box<dyn Trait>` over generics (`T: Trait`)?**
- [ ] When you want the fastest possible code.
- [x] When you need a heterogeneous collection of types that all implement the same trait, or when the concrete type is not known at compile time.
- [ ] When the trait has generic methods.
- [ ] `Box<dyn Trait>` is always preferred over generics.

**Q3. What does `RefCell<T>` provide that a plain `&mut T` does not?**
- [ ] Multi-threaded access.
- [x] Interior mutability — the ability to mutate data through a shared (immutable) reference, with borrow checks enforced at runtime.
- [ ] Faster access to the inner value.
- [ ] Automatic garbage collection.

**Q4. Which of the following closures captures its environment by taking ownership?**
- [ ] `|x| x + 1`
- [ ] `|| println!("{}", y)` where `y` is in scope
- [x] `move || println!("{}", y)` where `y` is in scope
- [ ] `|x: i32| -> i32 { x }`

**Q5. In Rust's module system, what does `pub(crate)` mean?**
- [ ] The item is visible everywhere, including to external crates.
- [x] The item is visible to any module within this crate, but not to external crates.
- [ ] The item is visible only to the parent module.
- [ ] The item is visible only within the current module.

**Q6. What is the purpose of the `?` operator in a function that returns `Result<T, E>`?**
- [ ] It marks the expression as optional and converts it to an `Option`.
- [x] If the expression is `Err(e)`, it immediately returns `Err(e.into())` from the enclosing function; if it is `Ok(v)`, it unwraps to `v`.
- [ ] It panics with the error message if the expression is `Err`.
- [ ] It retries the expression until it returns `Ok`.

**Q7. Which channel type does `std::sync::mpsc` provide?**
- [ ] Single-producer, single-consumer.
- [x] Multi-producer, single-consumer.
- [ ] Multi-producer, multi-consumer.
- [ ] Single-producer, multi-consumer.
