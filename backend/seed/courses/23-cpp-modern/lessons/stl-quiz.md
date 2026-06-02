# Quiz: STL Containers, Algorithms, and Iterators

**Q1. Which STL container gives O(1) average-case lookup by key?**
- [ ] `std::map`
- [x] `std::unordered_map`
- [ ] `std::vector`
- [ ] `std::list`

**Q2. `std::vector` stores its elements:**
- [ ] In a linked list of nodes
- [ ] In a balanced binary search tree
- [x] In a contiguous heap-allocated array
- [ ] On the call stack

**Q3. What does `std::sort` require of its iterator arguments?**
- [ ] Input iterators
- [ ] Forward iterators
- [ ] Bidirectional iterators
- [x] Random-access iterators

**Q4. Which algorithm finds the first element satisfying a predicate?**
- [ ] `std::search`
- [ ] `std::count_if`
- [x] `std::find_if`
- [ ] `std::partition`

**Q5. What is the result of calling `std::accumulate({1,2,3,4}, 0)`?**
- [ ] `{1,3,6,10}`
- [ ] 24
- [x] 10
- [ ] 0

**Q6. Which insert iterator adaptor calls `push_back` on the container?**
- [x] `std::back_inserter`
- [ ] `std::front_inserter`
- [ ] `std::inserter`
- [ ] `std::begin_inserter`

**Q7. `std::map` iterates its keys in which order?**
- [ ] Insertion order
- [ ] Random order
- [x] Sorted (ascending) order
- [ ] Hash order

**Q8. A lambda `[&](int x){ return x > threshold; }` captures `threshold` by:**
- [ ] Value (copy)
- [x] Reference
- [ ] Pointer
- [ ] Move
