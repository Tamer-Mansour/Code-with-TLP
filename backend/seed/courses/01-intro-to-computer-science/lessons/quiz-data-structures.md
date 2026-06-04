# Quiz: Strings, Lists, Tuples, and Dictionaries

---

**Question 1.** Which of the following is immutable in Python?

- [ ] list
- [ ] dict
- [x] tuple
- [ ] set

---

**Question 2.** What does the following code print?

```python
a = [1, 2, 3]
b = a
b.append(4)
print(a)
```

- [ ] [1, 2, 3]
- [x] [1, 2, 3, 4]
- [ ] [4]
- [ ] Error

---

**Question 3.** How do you safely access a dictionary key that might not exist?

- [ ] `d[key]`
- [x] `d.get(key, default)`
- [ ] `d.find(key)`
- [ ] `key in d[key]`

---

**Question 4.** What does `"hello"[1:4]` evaluate to?

- [ ] "hel"
- [x] "ell"
- [ ] "ello"
- [ ] "hell"

---

**Question 5.** What is the key difference between a list and a tuple?

- [ ] Lists are ordered; tuples are not
- [ ] Tuples can hold more elements than lists
- [x] Lists are mutable; tuples are immutable
- [ ] Tuples are faster to iterate than lists

---

**Question 6.** After running the code below, what is the value of `c`?

```python
a = [10, 20, 30]
c = a.copy()
c.append(40)
```

- [x] [10, 20, 30, 40]
- [ ] [10, 20, 30]
- [ ] The same as `a` which is also [10, 20, 30, 40]
- [ ] Error

---

**Question 7.** What is the average-case time complexity of looking up a key in a Python dictionary?

- [ ] O(n)
- [ ] O(log n)
- [x] O(1)
- [ ] O(n²)

---

**Question 8.** Which data type CAN be used as a dictionary key?

- [ ] list
- [ ] dict
- [x] tuple containing only integers
- [ ] set
