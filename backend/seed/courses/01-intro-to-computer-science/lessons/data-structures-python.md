# Strings, Lists, Tuples, and Dictionaries

Python provides four essential built-in data structures that every programmer must master. Understanding their differences — especially **mutability** — prevents some of the most confusing bugs in Python.

## Strings

A **string** is an immutable sequence of characters. Immutable means you cannot change it in place — any "modification" creates a new string.

```python
s = "hello"
print(s[0])       # 'h'  — indexing
print(s[1:4])     # 'ell' — slicing [start:stop] (stop is exclusive)
print(s[::-1])    # 'olleh' — reverse with step -1
print(len(s))     # 5

# Strings are immutable:
s[0] = 'H'        # TypeError: 'str' object does not support item assignment
new_s = 'H' + s[1:]   # create a new string instead
```

Key string methods: `upper()`, `lower()`, `strip()`, `split()`, `join()`, `replace()`, `find()`, `startswith()`, `endswith()`.

## Lists

A **list** is a mutable, ordered sequence. You can change elements in place.

```python
fruits = ["apple", "banana", "cherry"]
fruits.append("date")          # add to end
fruits.insert(1, "avocado")    # insert at index 1
fruits.pop()                   # remove and return last element
fruits.pop(0)                  # remove and return element at index 0
fruits.sort()                  # sort in place
fruits.remove("banana")        # remove first occurrence

# Slicing creates a new list
subset = fruits[1:3]
```

### Mutability: The Aliasing Trap

Because lists are mutable, assigning a list to a new variable does **not** copy it — both names point to the same object:

```python
a = [1, 2, 3]
b = a             # b is an ALIAS — same object
b.append(4)
print(a)          # [1, 2, 3, 4] — a changed too!

# To get an independent copy:
c = a.copy()      # or a[:]
c.append(5)
print(a)          # [1, 2, 3, 4] — a is unchanged
```

This is one of the most common Python pitfalls. When in doubt, copy explicitly.

## Tuples

A **tuple** is an immutable ordered sequence. Use tuples for data that should not change.

```python
point = (3, 4)
x, y = point      # tuple unpacking
print(x, y)       # 3 4

rgb = (255, 128, 0)
# rgb[0] = 100    # TypeError: tuples are immutable
```

Tuples are slightly faster than lists and can be used as dictionary keys (since they are immutable and therefore hashable). Use a tuple when your data is fixed, a list when it will grow or change.

## Dictionaries

A **dictionary** maps **keys** to **values**. Keys must be immutable (strings, numbers, tuples); values can be anything.

```python
person = {"name": "Alice", "age": 30, "city": "Cairo"}

# Access
print(person["name"])          # Alice
print(person.get("phone", "N/A"))  # N/A — safe access with default

# Modify and add
person["age"] = 31
person["email"] = "alice@example.com"

# Delete
del person["city"]

# Iterating
for key in person:
    print(key, "->", person[key])

for key, value in person.items():
    print(f"{key}: {value}")

# Check membership
"name" in person       # True
"phone" in person      # False
```

Word frequency counter — a classic dictionary use case:

```python
text = "the cat sat on the mat the cat"
freq = {}
for word in text.split():
    freq[word] = freq.get(word, 0) + 1
print(freq)   # {'the': 3, 'cat': 2, 'sat': 1, 'on': 1, 'mat': 1}
```

## Mutability Summary

| Type | Mutable? | Ordered? | Duplicate values? | Use as dict key? |
|------|----------|----------|-------------------|-----------------|
| `str` | No | Yes | Yes | Yes |
| `list` | Yes | Yes | Yes | No |
| `tuple` | No | Yes | Yes | Yes |
| `dict` | Yes (values) | Yes (Python 3.7+) | Keys: No; Values: Yes | No |

## Common Misconceptions

> "Variables store values like labeled boxes."

In Python, variables are **references** to objects. `b = a` makes `b` point to the same object `a` points to. For mutable objects like lists, this means changes through one name are visible through the other. For immutable objects like integers and strings, rebinding one name never affects the other.

## Further Reading

- **Think Python (Ch. 8, 10, 11, 12)** — https://greenteapress.com/wp/think-python-2e/
- **MIT 6.0001 Lecture 6: Recursion and Dictionaries** — https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/
- **How to Think Like a Computer Scientist: Interactive Edition** — https://runestone.academy/ns/books/published/thinkcspy/index.html

## Key Takeaways

- Strings and tuples are **immutable** — you cannot change them in place; you create new ones.
- Lists and dictionaries are **mutable** — changes propagate through all aliases.
- Assigning a list to a new variable creates an **alias**, not a copy. Use `.copy()` or `[:]` to copy.
- Dictionaries provide O(1) average-case lookups and are ideal for counting, grouping, and mapping.
