# Quiz: Data Structures

**Q1. Which of the following creates a set in Python?**
- [ ] `x = {}`
- [x] `x = {1, 2, 3}`
- [ ] `x = (1, 2, 3)`
- [ ] `x = [1, 2, 3]`

**Q2. What is the result of `[1, 2, 3].pop(0)`?**
- [x] `1`, and the list becomes `[2, 3]`
- [ ] `3`, and the list becomes `[1, 2]`
- [ ] `1`, and the list remains `[1, 2, 3]`
- [ ] A `TypeError`

**Q3. Tuples differ from lists in that tuples are:**
- [ ] Unordered
- [x] Immutable
- [ ] Unindexed
- [ ] Only for strings

**Q4. Given `d = {"a": 1, "b": 2}`, what does `d.get("c", 99)` return?**
- [ ] A `KeyError`
- [ ] `None`
- [x] `99`
- [ ] `"c"`

**Q5. What does the following code print?**
```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)
```
- [ ] `[1, 2, 3]`
- [x] `[1, 2, 3, 4]`
- [ ] `[4]`
- [ ] A `TypeError`

**Q6. Which list comprehension produces `[0, 2, 4, 6, 8]`?**
- [ ] `[i for i in range(10) if i % 2 != 0]`
- [ ] `[i * 2 for i in range(5)]`
- [x] `[i for i in range(10) if i % 2 == 0]`
- [ ] `[i for i in range(0, 10, 3)]`

**Q7. `frozenset` differs from `set` because a `frozenset` is:**
- [ ] Ordered
- [ ] Mutable
- [x] Immutable and hashable
- [ ] A type of tuple
