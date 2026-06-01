# Quiz: Rust Basics

**Q1. Rust manages memory with:**
- [ ] A garbage collector
- [ ] Manual malloc/free
- [x] Ownership rules enforced at compile time
- [ ] Reference counting only

**Q2. After `let s2 = s1;` where `s1: String`, you can use:**
- [ ] Both `s1` and `s2`
- [x] Only `s2`
- [ ] Only `s1`
- [ ] Neither

**Q3. The rule for borrowing is:**
- [ ] One reference at a time (mut or immut)
- [x] One mutable XOR any number of immutable, at the same time
- [ ] Up to 16 references
- [ ] Any references freely

**Q4. The Rust REPL is:**
- [ ] `rust`
- [x] There is no official REPL; use `cargo run` on a tiny project
- [ ] `cargo repl`
- [ ] `irust` (it's third-party)

**Q5. The macro `println!` is:**
- [ ] A function
- [ ] An attribute
- [x] A macro (note the `!`)
- [ ] A trait method

**Q6. Which command builds the optimized binary?**
- [ ] `cargo build`
- [ ] `cargo run --opt`
- [x] `cargo build --release`
- [ ] `rustc --release`
