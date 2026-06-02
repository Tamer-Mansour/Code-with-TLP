# Quiz: The Standard Template Library: Containers

**Q1. What is the amortised time complexity of `std::vector::push_back`?**

- [ ] O(N)
- [x] O(1)
- [ ] O(log N)
- [ ] O(N log N)

Each `push_back` is O(1) amortised because the vector doubles its capacity on reallocation, so the total cost of N pushes is O(N) — spread across all pushes, each costs O(1) on average.

---

**Q2. Which of the following operations is NOT valid on `std::list` in O(1) given an iterator `it` pointing into the list?**

- [ ] `list.erase(it)`
- [ ] `list.insert(it, value)`
- [x] `list[5]`
- [ ] `list.splice(it, other_list)`

`std::list` does not support random-access indexing with `operator[]`. It is a doubly-linked list; reaching the N-th element requires O(N) traversal from either end.

---

**Q3. What happens when you call `std::unordered_map::operator[]` with a key that does not exist?**

- [ ] It throws `std::out_of_range`
- [ ] It returns a default-constructed temporary without modifying the map
- [x] It inserts a new entry with a default-constructed value and returns a reference to it
- [ ] It returns `nullptr`

`operator[]` on `unordered_map` (and `map`) always inserts a default-constructed value if the key is absent. Use `find()` or `contains()` (C++20) for non-mutating lookups.

---

**Q4. You need to store a sorted list of unique integers and efficiently answer "is X in the set?" queries in O(log N). Which container should you use?**

- [ ] `std::vector<int>` (unsorted)
- [ ] `std::list<int>`
- [x] `std::set<int>`
- [ ] `std::deque<int>`

`std::set<int>` is a red-black tree that stores unique elements in sorted order and provides O(log N) insert, erase, and `count`/`find` operations.

---

**Q5. After calling `v.push_back(x)` on a `std::vector v`, all previously obtained iterators and pointers into `v` may be invalidated. When does this definitely happen?**

- [ ] Every time `push_back` is called
- [ ] Only when `v.size() > 10`
- [x] Only when `v.size() == v.capacity()` before the call, causing reallocation
- [ ] Never — `push_back` never invalidates iterators

Reallocation — and thus iterator invalidation — occurs only when the vector runs out of capacity. If there is spare capacity, iterators to existing elements remain valid.

---

**Q6. Which container offers O(1) amortised insertion at both the front and the back, while also supporting O(1) random access by index?**

- [ ] `std::list`
- [ ] `std::vector`
- [x] `std::deque`
- [ ] `std::map`

`std::deque` (double-ended queue) is implemented as a segmented buffer that supports O(1) amortised push/pop at both ends and O(1) index access. `std::vector` is O(N) for front insertions, and `std::list` does not support O(1) random access.
