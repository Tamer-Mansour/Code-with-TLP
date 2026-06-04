# Control Flow and Iteration

Programs rarely run from top to bottom in a straight line. **Control flow** is how a program decides which instructions to execute, how many times to repeat them, and when to stop. Mastering control flow means mastering the logic that makes programs useful.

## Conditional Statements

A **conditional** lets your program make decisions. In Python, the fundamental construct is `if / elif / else`:

```python
score = 85

if score >= 90:
    print("A")
elif score >= 80:
    print("B")
elif score >= 70:
    print("C")
else:
    print("F")
```

Python evaluates conditions from top to bottom and executes **at most one** branch. Once a condition is `True`, the rest are skipped.

### Order of Conditions Matters

A classic mistake is putting a less-specific condition before a more-specific one:

```python
# WRONG — the combined check will never be reached
n = 15
if n % 3 == 0:
    print("Fizz")
elif n % 5 == 0:
    print("Buzz")
elif n % 15 == 0:         # dead code: if n % 15 == 0, then n % 3 == 0 fired first
    print("FizzBuzz")

# CORRECT — check the most specific condition first
if n % 15 == 0:
    print("FizzBuzz")
elif n % 3 == 0:
    print("Fizz")
elif n % 5 == 0:
    print("Buzz")
```

This ordering principle — most specific first — is the key insight behind the FizzBuzz problem.

## While Loops

A **while loop** repeats a block as long as its condition remains `True`.

```python
count = 1
while count <= 5:
    print(count)
    count += 1
# Prints 1, 2, 3, 4, 5
```

**Infinite loop warning:** if the condition never becomes `False`, the program runs forever. Always make sure the loop variable changes inside the loop.

## For Loops

A **for loop** iterates over a sequence — a range of numbers, a list, a string, or any iterable.

```python
# Range: 0-indexed, end is exclusive
for i in range(5):
    print(i)   # 0, 1, 2, 3, 4

# Iterating a list
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)

# Iterating with index
for i, fruit in enumerate(fruits):
    print(i, fruit)
```

`range(start, stop, step)` gives fine-grained control:

```python
for i in range(10, 0, -2):
    print(i)   # 10, 8, 6, 4, 2
```

## Loop Control: break and continue

- **`break`** exits the loop immediately.
- **`continue`** skips the rest of the current iteration and jumps to the next.

```python
# Find first even number
for n in [1, 3, 4, 7, 8]:
    if n % 2 == 0:
        print("First even:", n)
        break

# Print odd numbers only
for n in range(1, 11):
    if n % 2 == 0:
        continue
    print(n)   # 1, 3, 5, 7, 9
```

## Nested Loops

Loops can be placed inside other loops. The inner loop runs to completion for **each** iteration of the outer loop.

```python
for row in range(1, 4):
    for col in range(1, 4):
        print(row * col, end=" ")
    print()   # newline after each row
# Output:
# 1 2 3
# 2 4 6
# 3 6 9
```

Nested loops are common in algorithms like bubble sort, matrix operations, and pattern printing.

## Common Misconception

A frequent mistake is writing `if` when you mean `elif`:

```python
# BUG: multiple independent ifs can all fire
x = 15
if x % 3 == 0:
    print("Divisible by 3")
if x % 5 == 0:
    print("Divisible by 5")
# Both print! That may or may not be what you want.
```

Using `elif` creates a mutually exclusive choice; using multiple `if` statements creates independent checks.

## Further Reading

- **Think Python (Ch. 5 & 7)** by Allen B. Downey — https://greenteapress.com/wp/think-python-2e/
- **How to Think Like a Computer Scientist: Interactive Edition** — https://runestone.academy/ns/books/published/thinkcspy/index.html (run and experiment with loops in-browser)
- **MIT 6.0001 Lecture 3: String Manipulation, Guess & Check** — https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/

## Key Takeaways

- `if / elif / else` creates mutually exclusive branches; order conditions from most specific to least specific.
- `while` loops repeat while a condition is true; `for` loops iterate over a sequence.
- `break` exits a loop early; `continue` skips to the next iteration.
- Nested loops have O(n²) iterations — think carefully about performance when nesting.
