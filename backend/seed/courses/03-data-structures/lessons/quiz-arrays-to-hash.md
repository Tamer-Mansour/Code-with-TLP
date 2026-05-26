# Quiz: Arrays, Lists, Stacks, Queues & Hash Tables

**Q1. What is the time complexity of accessing an element by index in a dynamic array?**
- [ ] O(n)
- [x] O(1)
- [ ] O(log n)
- [ ] O(n log n)

**Q2. What is the amortised time complexity of appending to a Python list?**
- [ ] O(n) — always copies the whole array
- [ ] O(log n) — binary search for insertion point
- [x] O(1) — amortised via exponential growth
- [ ] O(n²) — quadratic due to shifting

**Q3. Which operation is O(n) on a Python list but O(1) on a collections.deque?**
- [ ] Appending to the right end
- [ ] Peeking at the right end
- [x] Removing from the left end (front)
- [ ] Checking the length

**Q4. A stack uses which access order?**
- [ ] FIFO — first in, first out
- [x] LIFO — last in, first out
- [ ] Random access by index
- [ ] Priority order based on value

**Q5. You implement a queue using two stacks. What is the amortised time complexity of a single dequeue?**
- [ ] O(n) — always transfers the whole inbox
- [ ] O(log n)
- [x] O(1) amortised — each element transfers at most once
- [ ] O(n²)

**Q6. What causes a hash table's lookup to degrade from O(1) to O(n)?**
- [ ] The hash function returns floating-point numbers
- [ ] The capacity exceeds the number of stored keys
- [x] All keys hash to the same bucket (extreme collisions)
- [ ] The keys are stored in sorted order

**Q7. The load factor α of a hash table is defined as:**
- [ ] capacity / number_of_stored_items
- [x] number_of_stored_items / capacity
- [ ] number_of_collisions / number_of_stored_items
- [ ] hash_value % capacity

**Q8. In open-addressing with linear probing, why are tombstone markers used instead of clearing deleted slots?**
- [ ] To save memory by not zeroing out the slot
- [ ] To speed up subsequent insertions
- [x] To prevent probe chains from breaking — lookups skip tombstones instead of stopping
- [ ] Because Python's dict requires it internally
