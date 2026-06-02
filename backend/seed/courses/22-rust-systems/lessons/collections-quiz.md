# Quiz: Collections and Iterators

**Q1. Which iterator method should you use to transform every element in a collection into a new value?**
- [ ] `filter()`
- [x] `map()`
- [ ] `fold()`
- [ ] `flatten()`

**Q2. What does `v.iter()` yield, compared to `v.into_iter()`?**
- [x] `iter()` yields immutable references (`&T`); `into_iter()` consumes the collection and yields owned values (`T`).
- [ ] They are identical.
- [ ] `iter()` consumes the collection; `into_iter()` borrows it.
- [ ] `iter()` yields mutable references; `into_iter()` yields immutable references.

**Q3. What is the result of the following code?**

```rust
let v = vec![1, 2, 3, 4];
let x: i32 = v.iter().filter(|&&n| n % 2 == 0).map(|&n| n * n).sum();
```

- [ ] 6
- [ ] 10
- [x] 20
- [ ] 25

**Q4. Which HashMap pattern inserts a value only if the key does not already exist?**
- [ ] `scores.insert(key, value)`
- [x] `scores.entry(key).or_insert(value)`
- [ ] `scores.get_or_insert(key, value)`
- [ ] `scores.set_default(key, value)`

**Q5. What is a key property of iterator adapters in Rust?**
- [ ] They allocate a new `Vec` for each step in the chain.
- [ ] They run eagerly and immediately process the collection.
- [x] They are lazy — no computation happens until a consumer is called.
- [ ] They can only be used with numeric types.

**Q6. You want to remove duplicates from a `Vec<i32>`. Which approach is most idiomatic?**
- [ ] Manually compare every pair with a nested `for` loop.
- [x] Collect the elements into a `HashSet<i32>`, then back into a `Vec` if order doesn't matter.
- [ ] Call `v.dedup()` on the unsorted vector.
- [ ] Use `v.retain()` with a closure that checks a counter.

**Q7. What does `enumerate()` return for each iteration?**
- [ ] The element and its memory address.
- [x] A tuple `(usize_index, element_reference)`.
- [ ] The element and the total count of remaining elements.
- [ ] A pair of consecutive elements.
