"""
Seed file for "Python Programming Fundamentals" course.
Subject: Programming Languages (slug: programming-languages)
8 modules · 24 lessons · 16 exercises · 80 test cases.

Run from the backend/ directory:
    python seed/python_basics_seed.py
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models import Base, Course, Difficulty, Exercise, Lesson, LessonType, Module, Subject, Tag, TestCase


# ─────────────────────────────────────────────
# Idempotent helpers
# ─────────────────────────────────────────────

def _subject(db: Session, slug: str) -> Subject | None:
    return db.scalar(select(Subject).where(Subject.slug == slug))


def _course(db: Session, slug: str) -> Course | None:
    return db.scalar(select(Course).where(Course.slug == slug))


def _ensure_subject(db: Session, slug: str, **kwargs) -> Subject:
    s = db.scalar(select(Subject).where(Subject.slug == slug))
    if s:
        return s
    s = Subject(slug=slug, **kwargs)
    db.add(s)
    db.flush()
    return s


def _ensure_course(db: Session, subject: Subject, slug: str, **kwargs) -> Course:
    c = db.scalar(select(Course).where(Course.slug == slug))
    if c:
        return c
    c = Course(subject_id=subject.id, slug=slug, **kwargs)
    db.add(c)
    db.flush()
    return c


def _module(db: Session, course: Course, title: str, order_index: int, summary: str = "") -> Module:
    m = db.scalar(select(Module).where(Module.course_id == course.id, Module.title == title))
    if m:
        return m
    m = Module(course_id=course.id, title=title, order_index=order_index, summary=summary)
    db.add(m)
    db.flush()
    return m


def _lesson(db: Session, module: Module, slug: str, **kwargs) -> Lesson:
    l = db.scalar(select(Lesson).where(Lesson.module_id == module.id, Lesson.slug == slug))
    if l:
        return l
    l = Lesson(module_id=module.id, slug=slug, **kwargs)
    db.add(l)
    db.flush()
    return l


def _exercise(db: Session, lesson: Lesson, slug: str, **kwargs) -> Exercise:
    e = db.scalar(select(Exercise).where(Exercise.slug == slug))
    if e:
        return e
    e = Exercise(lesson_id=lesson.id, slug=slug, **kwargs)
    db.add(e)
    db.flush()
    return e


def _cases(db: Session, exercise: Exercise, cases: list) -> None:
    if exercise.test_cases:
        return
    for i, (stdin, expected, hidden) in enumerate(cases):
        db.add(TestCase(
            exercise_id=exercise.id,
            name=f"case-{i + 1}",
            stdin=stdin,
            expected_stdout=expected,
            is_hidden=hidden,
            weight=1,
            order_index=i,
        ))


# ─────────────────────────────────────────────
# Module 1: Getting Started with Python
# ─────────────────────────────────────────────

def _build_module1(db: Session, course: Course) -> None:
    mod = _module(db, course, "Getting Started with Python", 1,
                  "Introduction to Python, its philosophy, and writing your first programs.")

    # Lesson 1 – Why Python? (reading)
    _lesson(db, mod, "python-intro",
            title="Why Python?",
            lesson_type=LessonType.reading,
            duration_minutes=10,
            order_index=1,
            content_md="""# Why Python?

## The Philosophy of Python

Python was created by Guido van Rossum and first released in 1991. Its guiding principles are captured in **The Zen of Python** (PEP 20), which you can read at any time by typing `import this` in the REPL:

```python
import this
# Beautiful is better than ugly.
# Explicit is better than implicit.
# Simple is better than complex.
# Readability counts.
```

Python values clarity over cleverness. Code is written once but read many times, so the language makes readability a first-class concern.

## Where Python Excels

Python is a general-purpose language used across many domains:

| Domain | Popular Libraries |
|---|---|
| Web development | Django, FastAPI, Flask |
| Data science & analytics | pandas, NumPy, matplotlib |
| Machine learning & AI | TensorFlow, PyTorch, scikit-learn |
| Automation & scripting | subprocess, paramiko, selenium |
| DevOps & cloud | boto3, Ansible, Fabric |

Its vast ecosystem and gentle learning curve make it the most popular language in the world according to the TIOBE Index and Stack Overflow Developer Survey.

## Interpreted vs Compiled

Python is an **interpreted** language. Unlike C or Go, there is no separate compile step — the CPython interpreter reads your source file and executes it line by line (after an internal compilation to bytecode). This makes iteration very fast: save the file, run it immediately.

**CPython** is the reference implementation (the one you download from python.org). **PyPy** is an alternative JIT-compiled implementation that can be 5–10× faster for long-running CPU-bound programs. For most learners and everyday scripting, CPython is the right choice.

## Python 2 vs Python 3

Python 2 reached end-of-life on January 1, 2020. All new projects should use **Python 3**. Key differences:

- `print` is a function in Python 3: `print("hello")`
- Integer division `/` returns a float in Python 3 (use `//` for floor division)
- Strings are Unicode by default in Python 3
- `range()` returns a lazy iterator in Python 3 (not a list)

## Installing Python

Download from [python.org](https://python.org). On most Linux distributions, Python 3 is pre-installed. Verify your installation:

```bash
python3 --version   # Linux/macOS
python --version    # Windows
```

## Running Python Code

You have two main ways to execute Python:

**1. Scripts** — save code in a `.py` file and run it:
```bash
python3 my_script.py
```

**2. The REPL (Read-Eval-Print Loop)** — an interactive shell for experimenting:
```bash
python3
>>> 2 + 2
4
>>> print("Hello, Python!")
Hello, Python!
>>> exit()
```

The REPL is invaluable for testing snippets, exploring APIs, and learning. Use it constantly as you work through this course.
""")

    # Lesson 2 – Python Syntax Fundamentals (reading)
    _lesson(db, mod, "python-syntax-basics",
            title="Python Syntax Fundamentals",
            lesson_type=LessonType.reading,
            duration_minutes=12,
            order_index=2,
            content_md="""# Python Syntax Fundamentals

## Indentation Is the Syntax

Python uses **indentation** (whitespace) to define code blocks instead of curly braces. This is not just style — it is mandatory syntax:

```python
if True:
    print("indented block")   # 4 spaces — correct
    print("still in block")
print("back to top level")
```

The standard is **4 spaces** per level (PEP 8). Never mix tabs and spaces — Python 3 will raise a `TabError`.

## Comments

```python
# Single-line comment

\"\"\"
Multi-line string used as a docstring or block comment.
Python has no dedicated block-comment syntax.
\"\"\"
```

## Built-in Functions You'll Use Constantly

```python
print("Hello")          # output to stdout
name = input("Name? ")  # read a line from stdin (returns str)
print(type(42))         # <class 'int'>
print(id(name))         # memory address of the object
```

## Variables and Dynamic Typing

Python is **dynamically typed** — you do not declare types; the interpreter infers them at runtime:

```python
x = 10           # int
x = "hello"      # now a str — same variable, different type
x = [1, 2, 3]    # now a list
```

Variables are just names that point to objects. Everything in Python — integers, strings, functions, classes — is an object.

## Naming Conventions (PEP 8)

| Style | Use for |
|---|---|
| `snake_case` | variables, functions, modules |
| `PascalCase` | classes |
| `SCREAMING_SNAKE` | constants |
| `_single_leading` | "private" by convention |

## Multiple Assignment and Unpacking

```python
a = b = c = 0          # chained assignment
x, y, z = 1, 2, 3      # tuple unpacking
first, *rest = [1, 2, 3, 4]  # starred unpacking: first=1, rest=[2,3,4]
```

## Augmented Assignment Operators

```python
n = 10
n += 5    # n = 15
n -= 3    # n = 12
n *= 2    # n = 24
n //= 5   # n = 4  (floor division)
n **= 3   # n = 64 (power)
n %= 10   # n = 4  (modulo)
```

Note: Python has no `++` or `--` operators.

## Everything Is an Object

This is not just a slogan. In Python, even integers have methods:

```python
print((255).bit_length())   # 8
print("hello".upper())      # HELLO
print([1,2,3].count(2))     # 1
```

Understanding this mental model is the key to writing idiomatic Python. When you assign `a = 5` and then `b = a`, both names refer to the same integer object in memory — use `id()` to verify.
""")

    # Lesson 3 – First Python Exercises (exercise)
    les3 = _lesson(db, mod, "python-hello-exercises",
                   title="First Python Exercises",
                   lesson_type=LessonType.exercise,
                   duration_minutes=15,
                   order_index=3,
                   content_md="Practice the basics: reading input, formatting output, and simple arithmetic.")

    # Exercise 1: Hello Name
    ex1 = _exercise(db, les3, "py-hello-name",
                    title="Hello, Full Name!",
                    difficulty=Difficulty.easy,
                    points=10,
                    time_limit_ms=3000,
                    memory_limit_mb=256,
                    is_published=True,
                    supported_languages=["python"],
                    prompt_md="""## Problem

Read a first name and a last name from two separate lines, then print a greeting that includes the full name and the total number of letters (excluding the space between first and last name).

## Input Format

- Line 1: first name (a single word, no spaces)
- Line 2: last name (a single word, no spaces)

## Output Format

```
Hello, FirstName LastName! You have N letters in your name.
```

Where `N` is `len(first) + len(last)`.

## Example

**Input**
```
Alice
Smith
```

**Output**
```
Hello, Alice Smith! You have 10 letters in your name.
```

## Constraints

- Each name is 1–50 characters, letters only.
""",
                    starter_code={"python": """first = input()
last = input()
# TODO: compute total letters and print the greeting
"""},
                    solution_code={"python": """first = input()
last = input()
total = len(first) + len(last)
print(f"Hello, {first} {last}! You have {total} letters in your name.")
"""})
    _cases(db, ex1, [
        ("Alice\nSmith",      "Hello, Alice Smith! You have 10 letters in your name.", False),
        ("John\nDoe",         "Hello, John Doe! You have 6 letters in your name.",     False),
        ("Ada\nLovelace",     "Hello, Ada Lovelace! You have 11 letters in your name.", True),
        ("Muhammad\nAli",     "Hello, Muhammad Ali! You have 11 letters in your name.", True),
    ])

    # Exercise 2: Temperature Converter
    ex2 = _exercise(db, les3, "py-temperature-converter",
                    title="Temperature Converter",
                    difficulty=Difficulty.easy,
                    points=10,
                    time_limit_ms=3000,
                    memory_limit_mb=256,
                    is_published=True,
                    supported_languages=["python"],
                    prompt_md="""## Problem

Read a temperature and its unit, then convert it to the other unit and print the result.

- Celsius → Fahrenheit: `F = C × 9/5 + 32`
- Fahrenheit → Celsius: `C = (F − 32) × 5/9`

## Input Format

A single line with a floating-point number and a unit letter separated by a space:
```
<value> <C|F>
```

## Output Format

```
<result> F
```
or
```
<result> C
```

Print the result rounded to **one decimal place**.

## Example

**Input**
```
25 C
```
**Output**
```
77.0 F
```

**Input**
```
98.6 F
```
**Output**
```
37.0 C
```

## Constraints

- −500 ≤ value ≤ 500
- Unit is exactly `C` or `F` (uppercase)
""",
                    starter_code={"python": """line = input().split()
value = float(line[0])
unit = line[1]
# TODO: convert and print
"""},
                    solution_code={"python": """line = input().split()
value = float(line[0])
unit = line[1]
if unit == "C":
    result = value * 9 / 5 + 32
    print(f"{result:.1f} F")
else:
    result = (value - 32) * 5 / 9
    print(f"{result:.1f} C")
"""})
    _cases(db, ex2, [
        ("25 C",    "77.0 F",  False),
        ("98.6 F",  "37.0 C",  False),
        ("0 C",     "32.0 F",  False),
        ("100 C",   "212.0 F", True),
        ("32 F",    "0.0 C",   True),
    ])


# ─────────────────────────────────────────────
# Module 2: Data Types and Variables
# ─────────────────────────────────────────────

def _build_module2(db: Session, course: Course) -> None:
    mod = _module(db, course, "Data Types and Variables", 2,
                  "Deep dive into Python's built-in types: numbers, strings, booleans, and type conversion.")

    # Lesson 1 – Numbers, Strings, and Booleans (reading)
    _lesson(db, mod, "python-numbers-strings",
            title="Numbers, Strings, and Booleans",
            lesson_type=LessonType.reading,
            duration_minutes=15,
            order_index=1,
            content_md="""# Numbers, Strings, and Booleans

## Numeric Types

Python has three numeric types built in:

| Type | Example | Notes |
|---|---|---|
| `int` | `42`, `-7`, `0xFF` | Arbitrary precision — no overflow |
| `float` | `3.14`, `1e-4` | IEEE 754 double precision |
| `complex` | `2+3j` | Real + imaginary parts |

### Arithmetic Operators

```python
a, b = 17, 5
print(a + b)   # 22 — addition
print(a - b)   # 12 — subtraction
print(a * b)   # 85 — multiplication
print(a / b)   # 3.4 — true division (always float)
print(a // b)  # 3   — floor division
print(a % b)   # 2   — modulo
print(a ** b)  # 1419857 — exponentiation
```

The `math` module gives you `sqrt`, `ceil`, `floor`, `log`, `sin`, and many more:

```python
import math
print(math.sqrt(16))    # 4.0
print(math.ceil(3.1))   # 4
print(math.pi)          # 3.141592653589793
```

## Strings

Strings are immutable sequences of Unicode characters. You can create them with single or double quotes.

### f-strings (Recommended)

```python
name = "Alice"
age = 30
print(f"Hello, {name}! You are {age} years old.")
print(f"Pi ≈ {math.pi:.4f}")   # format spec after the colon
```

### Other Formatting Styles

```python
"Hello, {}!".format(name)       # str.format()
"Hello, %s!" % name             # %-formatting (legacy)
```

### Useful String Methods

```python
s = "  Hello, World!  "
s.upper()           # "  HELLO, WORLD!  "
s.lower()           # "  hello, world!  "
s.strip()           # "Hello, World!"
s.split(",")        # ["  Hello", " World!  "]
", ".join(["a","b","c"])  # "a, b, c"
s.replace("World", "Python")
s.find("World")     # index or -1
s.startswith("  H") # True
```

### String Slicing

```python
s = "Python"
s[0]      # 'P'
s[-1]     # 'n'
s[1:4]    # 'yth'
s[::-1]   # 'nohtyP'  — reversed
```

### Multiline Strings

```python
text = \"\"\"Line one
Line two
Line three\"\"\"
```

## Booleans and None

```python
print(True and False)  # False
print(True or False)   # True
print(not True)        # False

# Truthiness — these are all falsy:
# False, None, 0, 0.0, "", [], {}, set()

if "":
    print("won't run")
if "hello":
    print("non-empty strings are truthy")  # runs

x = None   # represents the absence of a value
print(x is None)  # True  (use 'is', not '==')
```
""")

    # Lesson 2 – Type Conversion (reading)
    _lesson(db, mod, "python-type-conversion",
            title="Type Conversion and Input Handling",
            lesson_type=LessonType.reading,
            duration_minutes=12,
            order_index=2,
            content_md="""# Type Conversion and Input Handling

## Implicit vs Explicit Conversion

Python performs **implicit** (automatic) conversion only in safe, non-lossy situations:

```python
print(1 + 2.5)    # 3.5 — int silently promoted to float
print(True + 1)   # 2   — bool is a subclass of int
```

For everything else you need **explicit** conversion:

```python
int("42")       # 42
float("3.14")   # 3.14
str(100)        # "100"
bool(0)         # False
bool("hello")   # True
```

### Common Pitfalls

```python
int("3.5")   # ValueError — int() cannot parse a decimal string
             # Fix: int(float("3.5")) → 3
int("0xFF", 16)  # 255 — specify base for hex/binary strings
```

## Reading Input in Competitive / Algorithmic Programming

`input()` always returns a **string**. You must convert explicitly:

```python
n = int(input())                       # single integer
a, b = map(int, input().split())       # two integers on one line
arr = list(map(int, input().split()))  # variable count of integers
```

### Reading Multiple Lines

```python
import sys

# Read all input at once (fast for large inputs):
data = sys.stdin.read().split()
n = int(data[0])
values = list(map(int, data[1:n+1]))
```

### Handling EOF with try/except

When the number of lines is unknown:

```python
import sys
lines = []
for line in sys.stdin:
    lines.append(line.rstrip())
```

Or use a try/except loop:

```python
results = []
try:
    while True:
        line = input()
        results.append(line)
except EOFError:
    pass
```

## Practical Tips

- Always convert `input()` to the appropriate type before arithmetic.
- Use `split()` without arguments to handle multiple spaces and leading/trailing whitespace.
- Prefer `sys.stdin.read()` in competitive programming — it is significantly faster than calling `input()` thousands of times.
- Remember that `int(float_string)` raises `ValueError`; use `int(float(s))` when the string may contain a decimal point.

## Type-Checking at Runtime

```python
x = 42
isinstance(x, int)          # True
isinstance(x, (int, float)) # True — check multiple types
type(x) is int              # True — exact type, no subclasses
```

Prefer `isinstance()` over `type()` when writing reusable code because it respects inheritance.
""")

    # Lesson 3 – Types and Strings Exercises (exercise)
    les3 = _lesson(db, mod, "python-types-exercises",
                   title="Types and Strings Exercises",
                   lesson_type=LessonType.exercise,
                   duration_minutes=20,
                   order_index=3,
                   content_md="Practice string manipulation, type conversion, and data aggregation.")

    # Exercise: Word Stats
    ex1 = _exercise(db, les3, "py-word-stats",
                    title="Word Statistics",
                    difficulty=Difficulty.easy,
                    points=10,
                    time_limit_ms=3000,
                    memory_limit_mb=256,
                    is_published=True,
                    supported_languages=["python"],
                    prompt_md="""## Problem

Read N words (one per line) and print four statistics about them.

## Input Format

- Line 1: integer N
- Next N lines: one word each (no spaces within a word)

## Output Format

Four lines:
```
Total words: N
Unique words: U
Longest word: W
First alphabetically: A
```

If multiple words tie for longest, print the one that appears **first** in the input.

## Example

**Input**
```
5
apple
banana
apple
cherry
date
```

**Output**
```
Total words: 5
Unique words: 4
Longest word: banana
First alphabetically: apple
```

## Constraints

- 1 ≤ N ≤ 1000
- Each word is 1–50 lowercase letters.
""",
                    starter_code={"python": """n = int(input())
words = [input() for _ in range(n)]
# TODO: compute and print stats
"""},
                    solution_code={"python": """n = int(input())
words = [input() for _ in range(n)]
unique = set(words)
longest = max(words, key=len)
first_alpha = min(words)
print(f"Total words: {n}")
print(f"Unique words: {len(unique)}")
print(f"Longest word: {longest}")
print(f"First alphabetically: {first_alpha}")
"""})
    _cases(db, ex1, [
        ("5\napple\nbanana\napple\ncherry\ndate",
         "Total words: 5\nUnique words: 4\nLongest word: banana\nFirst alphabetically: apple", False),
        ("3\nzebra\nant\nbird",
         "Total words: 3\nUnique words: 3\nLongest word: zebra\nFirst alphabetically: ant", False),
        ("1\nhello",
         "Total words: 1\nUnique words: 1\nLongest word: hello\nFirst alphabetically: hello", False),
        ("4\ncat\ndog\ncat\ndog",
         "Total words: 4\nUnique words: 2\nLongest word: cat\nFirst alphabetically: cat", True),
        ("3\nprogramming\ncode\nalgorithm",
         "Total words: 3\nUnique words: 3\nLongest word: programming\nFirst alphabetically: algorithm", True),
    ])

    # Exercise: Caesar Cipher
    ex2 = _exercise(db, les3, "py-caesar-cipher",
                    title="Caesar Cipher",
                    difficulty=Difficulty.easy,
                    points=10,
                    time_limit_ms=3000,
                    memory_limit_mb=256,
                    is_published=True,
                    supported_languages=["python"],
                    prompt_md="""## Problem

Implement the Caesar cipher: shift each letter forward in the alphabet by `shift` positions, wrapping around. Preserve case and leave non-letter characters unchanged.

## Input Format

- Line 1: integer `shift` (may be negative)
- Line 2: the message to encrypt

## Output Format

A single line: the encrypted message.

## Example

**Input**
```
3
Hello, World!
```

**Output**
```
Khoor, Zruog!
```

## Constraints

- -100 ≤ shift ≤ 100
- Message length 1–200; any printable ASCII characters.
""",
                    starter_code={"python": """shift = int(input())
message = input()
result = []
for ch in message:
    # TODO: shift letters, preserve case, leave non-letters unchanged
    result.append(ch)
print("".join(result))
"""},
                    solution_code={"python": """shift = int(input())
message = input()
result = []
for ch in message:
    if ch.isalpha():
        base = ord('A') if ch.isupper() else ord('a')
        result.append(chr((ord(ch) - base + shift) % 26 + base))
    else:
        result.append(ch)
print("".join(result))
"""})
    _cases(db, ex2, [
        ("3\nHello, World!",  "Khoor, Zruog!", False),
        ("0\nPython",         "Python",         False),
        ("1\nZz",             "Aa",             False),
        ("-3\nKhoor",         "Hello",          True),
        ("13\nROT13 test!",   "EBG13 grfg!",   True),
    ])


# ─────────────────────────────────────────────
# Module 3: Control Flow
# ─────────────────────────────────────────────

def _build_module3(db: Session, course: Course) -> None:
    mod = _module(db, course, "Control Flow", 3,
                  "Master conditionals and loops to direct the flow of your programs.")

    # Lesson 1 – if, elif, else (reading)
    _lesson(db, mod, "python-conditionals",
            title="if, elif, else",
            lesson_type=LessonType.reading,
            duration_minutes=15,
            order_index=1,
            content_md="""# Conditionals: if, elif, else

## Basic Structure

```python
x = 42
if x > 100:
    print("large")
elif x > 10:
    print("medium")   # this runs
else:
    print("small")
```

## Boolean Expressions and Comparison Operators

```python
==   !=   <   >   <=   >=   # comparison
and  or   not                # logical
in   not in                  # membership
is   is not                  # identity
```

### Short-Circuit Evaluation

```python
data = None
if data is not None and data["key"] == "value":
    ...  # safe: second condition only evaluated if data is not None
```

### Chained Comparisons

Python allows elegant chaining:

```python
if 0 < x < 100:    # equivalent to: x > 0 and x < 100
    print("in range")
```

## Ternary Expressions

```python
label = "even" if x % 2 == 0 else "odd"
```

## The Walrus Operator `:=` (Python 3.8+)

Assign and test in the same expression:

```python
import re
if m := re.search(r"\\d+", text):
    print(f"Found number: {m.group()}")
```

## match-case (Python 3.10+)

Structural pattern matching — Python's answer to `switch`:

```python
command = "quit"
match command:
    case "quit":
        print("Exiting")
    case "help":
        print("Available commands: quit, help")
    case _:
        print(f"Unknown command: {command}")
```

## Anti-Patterns to Avoid

```python
# BAD — redundant
if flag == True:
    ...
if flag == False:
    ...

# GOOD
if flag:
    ...
if not flag:
    ...

# BAD — double negatives are confusing
if not x not in collection:
    ...

# GOOD
if x in collection:
    ...
```

## Truthy and Falsy in Conditions

```python
items = []
if not items:          # True when list is empty
    print("no items")

name = ""
if name:               # False for empty string
    print(name)
```

Python's truthiness rules let you write expressive, concise conditions. Memorise the falsy values: `False`, `None`, `0`, `0.0`, `""`, `[]`, `{}`, `set()`.
""")

    # Lesson 2 – Loops (reading)
    _lesson(db, mod, "python-loops",
            title="for and while Loops",
            lesson_type=LessonType.reading,
            duration_minutes=15,
            order_index=2,
            content_md="""# for and while Loops

## The for Loop

Python's `for` loop iterates over any **iterable** — lists, strings, ranges, files, generators:

```python
for fruit in ["apple", "banana", "cherry"]:
    print(fruit)

for ch in "Python":
    print(ch)
```

### range()

```python
for i in range(5):          # 0 1 2 3 4
    print(i)

for i in range(2, 10, 2):   # 2 4 6 8
    print(i)

for i in range(10, 0, -1):  # 10 9 8 ... 1
    print(i)
```

### enumerate() — index + value

```python
fruits = ["apple", "banana", "cherry"]
for i, fruit in enumerate(fruits, start=1):
    print(f"{i}. {fruit}")
```

### zip() — parallel iteration

```python
names = ["Alice", "Bob"]
scores = [95, 87]
for name, score in zip(names, scores):
    print(f"{name}: {score}")
```

## while Loops

```python
n = 10
total = 0
while n > 0:
    total += n
    n -= 1
print(total)  # 55
```

### break and continue

```python
for i in range(10):
    if i == 3:
        continue   # skip 3
    if i == 7:
        break      # stop at 7
    print(i)
```

### Loop else Clause

The `else` block of a loop runs only if the loop was **not** terminated by `break`:

```python
for n in range(2, 10):
    for f in range(2, n):
        if n % f == 0:
            break
    else:
        print(f"{n} is prime")
```

## Nested Loops

```python
for i in range(3):
    for j in range(3):
        print(f"({i},{j})", end=" ")
    print()
```

## List Comprehensions (Preview)

A concise way to build lists from loops:

```python
squares = [x**2 for x in range(10)]
evens   = [x for x in range(20) if x % 2 == 0]
```

You will master comprehensions in a later module. For now, focus on reading and writing explicit `for` loops with full clarity.
""")

    # Lesson 3 – Control Flow Exercises (exercise)
    les3 = _lesson(db, mod, "python-control-flow-exercises",
                   title="Control Flow Exercises",
                   lesson_type=LessonType.exercise,
                   duration_minutes=20,
                   order_index=3,
                   content_md="Apply conditionals and loops to classic programming challenges.")

    # Exercise: FizzBuzz Variant
    ex1 = _exercise(db, les3, "py-fizzbuzz-variant",
                    title="Custom FizzBuzz",
                    difficulty=Difficulty.easy,
                    points=10,
                    time_limit_ms=3000,
                    memory_limit_mb=256,
                    is_published=True,
                    supported_languages=["python"],
                    prompt_md="""## Problem

Print numbers from A to B (inclusive). Replace multiples of 3 with `word1`, multiples of 5 with `word2`, and multiples of both 3 and 5 with `word1word2` (concatenated, no space).

## Input Format

```
A B word1 word2
```

All on one line separated by spaces.

## Output Format

One value per line (number or word).

## Example

**Input**
```
1 15 Fizz Buzz
```

**Output**
```
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
```

## Constraints

- 1 ≤ A ≤ B ≤ 1000
- 1 ≤ len(word1), len(word2) ≤ 20
""",
                    starter_code={"python": """parts = input().split()
a, b = int(parts[0]), int(parts[1])
word1, word2 = parts[2], parts[3]
for i in range(a, b + 1):
    # TODO: print word1, word2, word1+word2, or the number
    pass
"""},
                    solution_code={"python": """parts = input().split()
a, b = int(parts[0]), int(parts[1])
word1, word2 = parts[2], parts[3]
for i in range(a, b + 1):
    out = ""
    if i % 3 == 0:
        out += word1
    if i % 5 == 0:
        out += word2
    print(out if out else i)
"""})
    _cases(db, ex1, [
        ("1 15 Fizz Buzz",
         "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz", False),
        ("1 5 Foo Bar",
         "1\n2\nFoo\n4\nBar", False),
        ("15 15 Fizz Buzz",
         "FizzBuzz", False),
        ("1 6 Hello World",
         "1\n2\nHello\n4\nWorld\nHello", True),
        ("10 20 A B",
         "AB\n11\nA\n13\n14\nAB\n16\n17\nA\n19\nB", True),
    ])

    # Exercise: Number Pattern
    ex2 = _exercise(db, les3, "py-number-pattern",
                    title="Number Triangle Pattern",
                    difficulty=Difficulty.medium,
                    points=15,
                    time_limit_ms=3000,
                    memory_limit_mb=256,
                    is_published=True,
                    supported_languages=["python"],
                    prompt_md="""## Problem

Print a right-triangle number pattern. Row `i` (1-indexed) contains the numbers `1` through `i` separated by single spaces.

## Input Format

A single integer N.

## Output Format

N lines. Line i contains `1 2 3 ... i`.

## Example

**Input**
```
4
```

**Output**
```
1
1 2
1 2 3
1 2 3 4
```

## Constraints

- 1 ≤ N ≤ 20
""",
                    starter_code={"python": """n = int(input())
for i in range(1, n + 1):
    # TODO: print numbers 1 to i separated by spaces
    pass
"""},
                    solution_code={"python": """n = int(input())
for i in range(1, n + 1):
    print(" ".join(str(j) for j in range(1, i + 1)))
"""})
    _cases(db, ex2, [
        ("1",  "1",                     False),
        ("3",  "1\n1 2\n1 2 3",         False),
        ("4",  "1\n1 2\n1 2 3\n1 2 3 4", False),
        ("5",  "1\n1 2\n1 2 3\n1 2 3 4\n1 2 3 4 5", True),
    ])


# ─────────────────────────────────────────────
# Module 4: Functions
# ─────────────────────────────────────────────

def _build_module4(db: Session, course: Course) -> None:
    mod = _module(db, course, "Functions", 4,
                  "Write reusable, composable functions using Python's powerful function features.")

    # Lesson 1 – Defining and Calling Functions (reading)
    _lesson(db, mod, "python-functions",
            title="Defining and Calling Functions",
            lesson_type=LessonType.reading,
            duration_minutes=18,
            order_index=1,
            content_md="""# Defining and Calling Functions

## Basic Syntax

```python
def greet(name):
    \"\"\"Return a greeting string.\"\"\"   # docstring
    return f"Hello, {name}!"

print(greet("Alice"))   # Hello, Alice!
```

## Default Arguments

```python
def power(base, exponent=2):
    return base ** exponent

power(3)      # 9   (exponent defaults to 2)
power(3, 3)   # 27
```

**Caution:** Never use a mutable default argument:

```python
def append_to(item, lst=[]):   # BUG — list is shared across calls!
    lst.append(item)
    return lst

def append_to(item, lst=None): # CORRECT
    if lst is None:
        lst = []
    lst.append(item)
    return lst
```

## Keyword Arguments

```python
def connect(host, port=5432, ssl=False):
    ...

connect("localhost", ssl=True, port=5433)  # order doesn't matter with kwargs
```

## *args and **kwargs

```python
def total(*args):        # args is a tuple of positional arguments
    return sum(args)

def show(**kwargs):      # kwargs is a dict of keyword arguments
    for k, v in kwargs.items():
        print(f"{k} = {v}")

total(1, 2, 3, 4)          # 10
show(name="Alice", age=30)
```

## Type Annotations (PEP 484)

```python
def add(a: int, b: int) -> int:
    return a + b

def process(items: list[str]) -> dict[str, int]:
    return {item: len(item) for item in items}
```

Annotations are hints only — Python does not enforce them at runtime. Use `mypy` for static checking.

## Scope: The LEGB Rule

Python looks up names in this order:

1. **L**ocal — inside the current function
2. **E**nclosing — in any enclosing function scopes (closures)
3. **G**lobal — at the module level
4. **B**uilt-in — Python's built-in names (`len`, `print`, ...)

```python
x = "global"

def outer():
    x = "enclosing"
    def inner():
        x = "local"
        print(x)   # "local"
    inner()
    print(x)       # "enclosing"

outer()
print(x)           # "global"
```

## global and nonlocal

```python
counter = 0

def increment():
    global counter    # modify the module-level variable
    counter += 1

def make_counter():
    count = 0
    def inc():
        nonlocal count  # modify the enclosing function's variable
        count += 1
        return count
    return inc
```

## Functions Are First-Class Objects

```python
def double(x):
    return x * 2

apply = double           # assign function to a variable
apply(5)                 # 10

funcs = [double, abs]    # store in a list
for f in funcs:
    print(f(-3))         # -6, 3
```
""")

    # Lesson 2 – Lambda and Higher-Order Functions (reading)
    _lesson(db, mod, "python-lambdas-hof",
            title="Lambda and Higher-Order Functions",
            lesson_type=LessonType.reading,
            duration_minutes=15,
            order_index=2,
            content_md="""# Lambda and Higher-Order Functions

## Lambda Expressions

A `lambda` is an anonymous, single-expression function:

```python
square = lambda x: x ** 2
print(square(5))   # 25

# Useful inline with sorted/map/filter:
pairs = [(1, 'b'), (2, 'a'), (3, 'c')]
pairs.sort(key=lambda pair: pair[1])
# [(2, 'a'), (1, 'b'), (3, 'c')]
```

Lambdas are limited to a single expression. For anything more complex, use a named `def`.

## map(), filter(), sorted()

```python
nums = [1, 2, 3, 4, 5]

squares  = list(map(lambda x: x**2, nums))     # [1, 4, 9, 16, 25]
evens    = list(filter(lambda x: x % 2 == 0, nums))  # [2, 4]
descend  = sorted(nums, key=lambda x: -x)       # [5, 4, 3, 2, 1]
```

In modern Python, list comprehensions are often preferred over `map`/`filter` for clarity.

## functools.reduce()

```python
from functools import reduce
product = reduce(lambda acc, x: acc * x, [1,2,3,4,5])  # 120
```

## functools.partial()

Create a new function by pre-filling arguments:

```python
from functools import partial
def power(base, exp):
    return base ** exp

square = partial(power, exp=2)
cube   = partial(power, exp=3)
print(square(4))   # 16
print(cube(3))     # 27
```

## Closures and Factory Functions

A closure captures variables from its enclosing scope:

```python
def make_multiplier(n):
    def multiply(x):
        return x * n   # n is captured from the enclosing scope
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(5))   # 10
print(triple(5))   # 15
```

## Decorators

A decorator is a function that wraps another function to add behaviour:

```python
import time
from functools import wraps

def timer(func):
    @wraps(func)  # preserves __name__, __doc__
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_sum(n):
    return sum(range(n))

slow_sum(10_000_000)
```

`@timer` is syntactic sugar for `slow_sum = timer(slow_sum)`.

### Practical Decorator Examples

```python
def retry(times):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == times - 1:
                        raise
        return wrapper
    return decorator

@retry(3)
def unstable_api_call():
    ...
```
""")

    # Lesson 3 – Functions Exercises (exercise)
    les3 = _lesson(db, mod, "python-functions-exercises",
                   title="Functions Exercises",
                   lesson_type=LessonType.exercise,
                   duration_minutes=20,
                   order_index=3,
                   content_md="Practice recursion and memoization — core functional programming techniques.")

    # Exercise: Recursive Power
    ex1 = _exercise(db, les3, "py-recursive-power",
                    title="Recursive Power",
                    difficulty=Difficulty.easy,
                    points=10,
                    time_limit_ms=3000,
                    memory_limit_mb=256,
                    is_published=True,
                    supported_languages=["python"],
                    prompt_md="""## Problem

Compute `x` raised to the power `n` using **recursion**. Handle negative exponents: `x^(-n) = 1 / x^n`.

> **Note:** Do not use Python's built-in `**` operator or `pow()`. Implement the computation recursively yourself.

## Input Format

Two numbers on one line: `x n`
- `x` is a float
- `n` is an integer

## Output Format

The result as a float rounded to **6 decimal places**.

## Example

**Input**
```
2 10
```
**Output**
```
1024.000000
```

**Input**
```
2 -3
```
**Output**
```
0.125000
```

## Constraints

- -10 ≤ x ≤ 10, x ≠ 0
- -20 ≤ n ≤ 20
""",
                    starter_code={"python": """def power(x, n):
    # TODO: implement recursively without using ** or pow()
    pass

parts = input().split()
x, n = float(parts[0]), int(parts[1])
print(f"{power(x, n):.6f}")
"""},
                    solution_code={"python": """def power(x, n):
    if n == 0:
        return 1.0
    if n < 0:
        return 1.0 / power(x, -n)
    if n % 2 == 0:
        half = power(x, n // 2)
        return half * half
    return x * power(x, n - 1)

parts = input().split()
x, n = float(parts[0]), int(parts[1])
print(f"{power(x, n):.6f}")
"""})
    _cases(db, ex1, [
        ("2 10",    "1024.000000",  False),
        ("2 -3",    "0.125000",     False),
        ("3 0",     "1.000000",     False),
        ("5 3",     "125.000000",   True),
        ("2 -1",    "0.500000",     True),
    ])

    # Exercise: Memoized Fibonacci
    ex2 = _exercise(db, les3, "py-memoized-fibonacci",
                    title="Memoized Fibonacci",
                    difficulty=Difficulty.medium,
                    points=15,
                    time_limit_ms=3000,
                    memory_limit_mb=256,
                    is_published=True,
                    supported_languages=["python"],
                    prompt_md="""## Problem

Print the Nth Fibonacci number. Use memoization to handle large values of N efficiently.

The Fibonacci sequence: F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2).

## Input Format

A single integer N.

## Output Format

A single integer: F(N).

## Example

**Input**
```
10
```
**Output**
```
55
```

## Constraints

- 0 ≤ N ≤ 1000
""",
                    starter_code={"python": """import sys
sys.setrecursionlimit(2000)

memo = {}

def fib(n):
    # TODO: implement with memoization
    pass

n = int(input())
print(fib(n))
"""},
                    solution_code={"python": """import sys
sys.setrecursionlimit(2000)

memo = {}

def fib(n):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fib(n - 1) + fib(n - 2)
    return memo[n]

n = int(input())
print(fib(n))
"""})
    _cases(db, ex2, [
        ("0",    "0",                                                       False),
        ("1",    "1",                                                       False),
        ("10",   "55",                                                      False),
        ("50",   "12586269025",                                             True),
        ("100",  "354224848179261915075",                                   True),
    ])


# ─────────────────────────────────────────────
# Module 5: Lists, Tuples, and Dictionaries
# ─────────────────────────────────────────────

def _build_module5(db: Session, course: Course) -> None:
    mod = _module(db, course, "Lists, Tuples, and Dictionaries", 5,
                  "Python's core collection types: lists, tuples, dicts, and sets.")

    # Lesson 1 – Lists and Tuples (reading)
    _lesson(db, mod, "python-lists",
            title="Lists and Tuples",
            lesson_type=LessonType.reading,
            duration_minutes=20,
            order_index=1,
            content_md="""# Lists and Tuples

## Lists

A list is an **ordered, mutable** sequence:

```python
nums = [3, 1, 4, 1, 5, 9]
mixed = [1, "hello", True, None, [1, 2]]

# Indexing and slicing
nums[0]      # 3
nums[-1]     # 9
nums[1:4]    # [1, 4, 1]
nums[::2]    # [3, 4, 5]    every second element
nums[::-1]   # [9, 5, 1, 4, 1, 3]  reversed copy
```

### Common List Methods

```python
lst = [1, 2, 3]
lst.append(4)          # [1, 2, 3, 4]
lst.extend([5, 6])     # [1, 2, 3, 4, 5, 6]
lst.insert(0, 0)       # [0, 1, 2, 3, 4, 5, 6]
lst.remove(3)          # remove first occurrence of 3
lst.pop()              # removes and returns last element
lst.pop(0)             # removes and returns element at index 0
lst.sort()             # in-place sort
lst.sort(reverse=True) # descending
lst.reverse()          # in-place reverse
lst.index(2)           # first index of value 2
lst.count(1)           # number of occurrences of 1
```

### List Comprehensions

```python
squares  = [x**2 for x in range(10)]
filtered = [x for x in range(20) if x % 3 == 0]
matrix   = [[i*j for j in range(1,4)] for i in range(1,4)]
```

### 2D Lists (Grids)

```python
grid = [[0]*3 for _ in range(3)]  # 3×3 grid of zeros
grid[1][2] = 5
# [[0, 0, 0], [0, 0, 5], [0, 0, 0]]
```

**Note:** Never create a 2D grid with `[[0]*3]*3` — that creates three references to the same inner list.

## Tuples

A tuple is an **ordered, immutable** sequence:

```python
point = (3, 4)
rgb   = (255, 128, 0)
single = (42,)   # trailing comma required for single-element tuple
```

### Use Cases for Tuples

- Return multiple values from functions: `return x, y`
- Dictionary keys (tuples are hashable, lists are not)
- Named tuples for lightweight records

### Named Tuples

```python
from collections import namedtuple
Point = namedtuple('Point', ['x', 'y'])
p = Point(3, 4)
print(p.x, p.y)    # 3 4
print(p[0])        # 3 — still indexable
```

### Tuple Unpacking and Packing

```python
a, b = 1, 2          # swap
a, b = b, a

first, *rest = [1, 2, 3, 4, 5]
# first=1, rest=[2,3,4,5]

*head, last = [1, 2, 3, 4, 5]
# head=[1,2,3,4], last=5
```
""")

    # Lesson 2 – Dicts and Sets (reading)
    _lesson(db, mod, "python-dicts-sets",
            title="Dictionaries and Sets",
            lesson_type=LessonType.reading,
            duration_minutes=18,
            order_index=2,
            content_md="""# Dictionaries and Sets

## Dictionaries

A `dict` maps keys to values. In Python 3.7+ dicts maintain **insertion order**.

```python
person = {"name": "Alice", "age": 30, "city": "Cairo"}

# Access
person["name"]              # "Alice"
person.get("email", "N/A")  # "N/A"  — safe access with default

# Mutation
person["age"] = 31
person.setdefault("country", "Egypt")  # only adds if key absent

# Iteration
for k, v in person.items():
    print(f"{k}: {v}")
```

### Useful Dict Methods

```python
d = {"a": 1, "b": 2, "c": 3}
d.keys()    # dict_keys(['a', 'b', 'c'])
d.values()  # dict_values([1, 2, 3])
d.items()   # dict_items([('a', 1), ('b', 2), ('c', 3)])
d.pop("b")  # removes and returns 1
d.update({"d": 4, "e": 5})
```

### Dict Comprehensions

```python
squares = {x: x**2 for x in range(1, 6)}
# {1: 1, 2: 4, 3: 9, 4: 16, 5: 25}

inverted = {v: k for k, v in squares.items()}
```

### collections.defaultdict and Counter

```python
from collections import defaultdict, Counter

word_count = defaultdict(int)
for word in "the quick brown fox the fox".split():
    word_count[word] += 1

freq = Counter("the quick brown fox the fox".split())
freq.most_common(2)   # [('the', 2), ('fox', 2)]
```

## Sets

A `set` is an unordered collection of unique elements:

```python
s = {1, 2, 3, 4}
s.add(5)
s.discard(10)   # no error if absent (unlike remove())

# Set operations
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}
a | b   # {1,2,3,4,5,6}  — union
a & b   # {3,4}           — intersection
a - b   # {1,2}           — difference
a ^ b   # {1,2,5,6}       — symmetric difference
```

### frozenset

An immutable set (hashable, can be a dict key):

```python
fs = frozenset([1, 2, 3])
```

## When to Use Each Structure

| Structure | Use when |
|---|---|
| `list` | Ordered sequence, need indexing or sorting |
| `tuple` | Immutable record, multiple return values |
| `dict` | Key-value lookup, counting, grouping |
| `set` | Membership testing, deduplication, set math |

For performance: `x in set` is O(1); `x in list` is O(n). Use sets for fast membership tests.
""")

    # Lesson 3 – Collections Exercises (exercise)
    les3 = _lesson(db, mod, "python-collections-exercises",
                   title="Collections Exercises",
                   lesson_type=LessonType.exercise,
                   duration_minutes=25,
                   order_index=3,
                   content_md="Apply dicts, sets, and lists to medium-difficulty algorithmic problems.")

    # Exercise: Group Anagrams
    ex1 = _exercise(db, les3, "py-group-anagrams",
                    title="Group Anagrams",
                    difficulty=Difficulty.medium,
                    points=15,
                    time_limit_ms=3000,
                    memory_limit_mb=256,
                    is_published=True,
                    supported_languages=["python"],
                    prompt_md="""## Problem

Given N words, group them by anagram. Words are anagrams of each other if they contain the same letters (case-insensitive, all lowercase).

## Input Format

- Line 1: integer N
- Next N lines: one word each

## Output Format

Print each group on one line: words within a group sorted alphabetically and separated by spaces. Groups themselves are sorted by their smallest word alphabetically.

## Example

**Input**
```
6
eat
tea
tan
ate
nat
bat
```

**Output**
```
ate eat tea
bat
nat tan
```

## Constraints

- 1 ≤ N ≤ 500
- Each word is 1–20 lowercase letters.
""",
                    starter_code={"python": """from collections import defaultdict

n = int(input())
words = [input() for _ in range(n)]
groups = defaultdict(list)
# TODO: group anagrams and print sorted output
"""},
                    solution_code={"python": """from collections import defaultdict

n = int(input())
words = [input() for _ in range(n)]
groups = defaultdict(list)
for word in words:
    key = "".join(sorted(word))
    groups[key].append(word)
result = [sorted(group) for group in groups.values()]
result.sort(key=lambda g: g[0])
for group in result:
    print(" ".join(group))
"""})
    _cases(db, ex1, [
        ("6\neat\ntea\ntan\nate\nnat\nbat",
         "ate eat tea\nbat\nnat tan", False),
        ("3\nabc\nbca\nxyz",
         "abc bca\nxyz", False),
        ("1\nhello",
         "hello", False),
        ("4\ncat\ndog\ntac\ngod",
         "cat tac\ndog god", True),
        ("5\nlisten\nsilent\nenlist\nworld\nword",
         "enlist listen silent\nword world", True),
    ])

    # Exercise: Sliding Window Maximum
    ex2 = _exercise(db, les3, "py-sliding-window-max",
                    title="Sliding Window Maximum",
                    difficulty=Difficulty.medium,
                    points=15,
                    time_limit_ms=3000,
                    memory_limit_mb=256,
                    is_published=True,
                    supported_languages=["python"],
                    prompt_md="""## Problem

Given an array of N integers and a window size K, find the maximum value in every contiguous window of size K as the window slides from left to right.

## Input Format

- Line 1: integer N
- Line 2: N space-separated integers
- Line 3: integer K

## Output Format

A single line: the maximum of each window separated by spaces. There are N-K+1 windows total.

## Example

**Input**
```
8
1 3 -1 -3 5 3 6 7
3
```

**Output**
```
3 3 5 5 6 7
```

## Constraints

- 1 ≤ K ≤ N ≤ 10000
- -10^4 ≤ each element ≤ 10^4
""",
                    starter_code={"python": """from collections import deque

n = int(input())
arr = list(map(int, input().split()))
k = int(input())
# TODO: compute sliding window max using a deque
"""},
                    solution_code={"python": """from collections import deque

n = int(input())
arr = list(map(int, input().split()))
k = int(input())

dq = deque()  # stores indices, front is the max
result = []
for i in range(n):
    # Remove indices outside window
    while dq and dq[0] < i - k + 1:
        dq.popleft()
    # Remove smaller elements from back
    while dq and arr[dq[-1]] < arr[i]:
        dq.pop()
    dq.append(i)
    if i >= k - 1:
        result.append(str(arr[dq[0]]))
print(" ".join(result))
"""})
    _cases(db, ex2, [
        ("8\n1 3 -1 -3 5 3 6 7\n3",   "3 3 5 5 6 7", False),
        ("5\n1 2 3 4 5\n1",            "1 2 3 4 5",   False),
        ("5\n5 4 3 2 1\n3",            "5 4 3",       False),
        ("6\n2 1 5 3 6 4\n2",          "2 5 5 6 6",   True),
        ("4\n1 1 1 1\n4",              "1",            True),
    ])


# ─────────────────────────────────────────────
# Module 6: Object-Oriented Programming
# ─────────────────────────────────────────────

def _build_module6(db: Session, course: Course) -> None:
    mod = _module(db, course, "Object-Oriented Programming", 6,
                  "Design and build classes with Python's full OOP toolkit.")

    # Lesson 1 – Classes and Objects (reading)
    _lesson(db, mod, "python-classes",
            title="Classes and Objects",
            lesson_type=LessonType.reading,
            duration_minutes=22,
            order_index=1,
            content_md="""# Classes and Objects

## Defining a Class

```python
class BankAccount:
    interest_rate = 0.02   # class variable — shared by all instances

    def __init__(self, owner: str, balance: float = 0.0):
        self.owner = owner       # instance variable
        self.balance = balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit must be positive")
        self.balance += amount

    def withdraw(self, amount: float) -> float:
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        return amount
```

## Special (Dunder) Methods

```python
    def __str__(self) -> str:
        return f"Account({self.owner}, ${self.balance:.2f})"

    def __repr__(self) -> str:
        return f"BankAccount(owner={self.owner!r}, balance={self.balance})"

    def __eq__(self, other) -> bool:
        return isinstance(other, BankAccount) and self.owner == other.owner

    def __hash__(self) -> int:
        return hash(self.owner)
```

`__str__` is for end-user output (`print`); `__repr__` is for developers and debugging.

## @property

Expose computed attributes without breaking the interface:

```python
class Circle:
    def __init__(self, radius: float):
        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @radius.setter
    def radius(self, value: float) -> None:
        if value < 0:
            raise ValueError("Radius cannot be negative")
        self._radius = value

    @property
    def area(self) -> float:
        import math
        return math.pi * self._radius ** 2
```

## @classmethod and @staticmethod

```python
class Employee:
    _count = 0

    def __init__(self, name):
        self.name = name
        Employee._count += 1

    @classmethod
    def get_count(cls) -> int:
        return cls._count   # cls is the class itself

    @staticmethod
    def validate_name(name: str) -> bool:
        return bool(name) and name.isalpha()
```

- `@classmethod` receives the class as first argument (`cls`); used for factory methods and class-level state.
- `@staticmethod` receives no implicit argument; essentially a namespaced function.

## __slots__ for Memory Optimization

```python
class Point:
    __slots__ = ("x", "y")  # prevents __dict__ creation
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

Use `__slots__` when you create millions of small objects.
""")

    # Lesson 2 – Inheritance (reading)
    _lesson(db, mod, "python-inheritance",
            title="Inheritance and Polymorphism",
            lesson_type=LessonType.reading,
            duration_minutes=18,
            order_index=2,
            content_md="""# Inheritance and Polymorphism

## Single Inheritance

```python
class Animal:
    def __init__(self, name: str):
        self.name = name

    def speak(self) -> str:
        raise NotImplementedError

class Dog(Animal):
    def speak(self) -> str:
        return f"{self.name} says Woof!"

class Cat(Animal):
    def speak(self) -> str:
        return f"{self.name} says Meow!"

for animal in [Dog("Rex"), Cat("Whiskers")]:
    print(animal.speak())   # polymorphism
```

## super()

Call the parent class constructor or method:

```python
class ColoredDog(Dog):
    def __init__(self, name, color):
        super().__init__(name)   # calls Dog.__init__ → Animal.__init__
        self.color = color
```

## Method Resolution Order (MRO)

Python uses the C3 linearisation algorithm. Inspect it with:

```python
print(ColoredDog.__mro__)
```

## Multiple Inheritance

```python
class Flyable:
    def fly(self): return "Flying!"

class Swimmable:
    def swim(self): return "Swimming!"

class Duck(Animal, Flyable, Swimmable):
    def speak(self): return "Quack!"
```

Use multiple inheritance sparingly. Prefer composition when possible.

## Abstract Base Classes

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...

    @abstractmethod
    def perimeter(self) -> float: ...

class Rectangle(Shape):
    def __init__(self, w, h):
        self.w, self.h = w, h

    def area(self):        return self.w * self.h
    def perimeter(self):   return 2 * (self.w + self.h)
```

You cannot instantiate `Shape` directly — Python raises `TypeError`.

## isinstance() and issubclass()

```python
r = Rectangle(3, 4)
isinstance(r, Shape)       # True
isinstance(r, Rectangle)   # True
issubclass(Rectangle, Shape)  # True
```

## Duck Typing and Protocols (Python 3.8+)

```python
from typing import Protocol

class Drawable(Protocol):
    def draw(self) -> None: ...

def render(obj: Drawable) -> None:
    obj.draw()
```

With `Protocol`, any class that has a `draw()` method satisfies `Drawable` without explicit inheritance — this is structural subtyping.

## Operator Overloading

```python
class Vector:
    def __init__(self, x, y): self.x, self.y = x, y
    def __add__(self, other): return Vector(self.x+other.x, self.y+other.y)
    def __len__(self):  return 2
    def __iter__(self): yield self.x; yield self.y
    def __repr__(self): return f"Vector({self.x}, {self.y})"
```
""")

    # Lesson 3 – OOP Exercises (exercise)
    les3 = _lesson(db, mod, "python-oop-exercises",
                   title="OOP Exercises",
                   lesson_type=LessonType.exercise,
                   duration_minutes=25,
                   order_index=3,
                   content_md="Implement a stack class and a shape hierarchy from scratch.")

    # Exercise: Stack Class
    ex1 = _exercise(db, les3, "py-stack-class",
                    title="Stack Implementation",
                    difficulty=Difficulty.easy,
                    points=10,
                    time_limit_ms=3000,
                    memory_limit_mb=256,
                    is_published=True,
                    supported_languages=["python"],
                    prompt_md="""## Problem

Implement a `Stack` class with the following operations, then process commands from stdin.

**Operations:**
- `PUSH x` — push integer x onto the stack
- `POP` — print and remove the top element (print `"Empty"` if empty)
- `PEEK` — print the top element without removing (print `"Empty"` if empty)
- `SIZE` — print the number of elements
- `ISEMPTY` — print `"True"` or `"False"`

## Input Format

- Line 1: integer N (number of commands)
- Next N lines: one command each

## Output Format

Print the result of POP, PEEK, SIZE, and ISEMPTY commands (one per line). PUSH produces no output.

## Example

**Input**
```
7
PUSH 5
PUSH 3
PEEK
POP
POP
ISEMPTY
SIZE
```

**Output**
```
3
3
5
True
0
```

## Constraints

- 1 ≤ N ≤ 1000
- -10^6 ≤ pushed values ≤ 10^6
""",
                    starter_code={"python": """class Stack:
    def __init__(self):
        self._data = []

    def push(self, x):
        pass  # TODO

    def pop(self):
        pass  # TODO

    def peek(self):
        pass  # TODO

    def is_empty(self):
        pass  # TODO

    def size(self):
        pass  # TODO

stack = Stack()
n = int(input())
for _ in range(n):
    cmd = input().split()
    # TODO: process commands
"""},
                    solution_code={"python": """class Stack:
    def __init__(self):
        self._data = []

    def push(self, x):
        self._data.append(x)

    def pop(self):
        if self._data:
            return self._data.pop()
        return None

    def peek(self):
        if self._data:
            return self._data[-1]
        return None

    def is_empty(self):
        return len(self._data) == 0

    def size(self):
        return len(self._data)

stack = Stack()
n = int(input())
for _ in range(n):
    parts = input().split()
    cmd = parts[0]
    if cmd == "PUSH":
        stack.push(int(parts[1]))
    elif cmd == "POP":
        val = stack.pop()
        print(val if val is not None else "Empty")
    elif cmd == "PEEK":
        val = stack.peek()
        print(val if val is not None else "Empty")
    elif cmd == "SIZE":
        print(stack.size())
    elif cmd == "ISEMPTY":
        print(stack.is_empty())
"""})
    _cases(db, ex1, [
        ("7\nPUSH 5\nPUSH 3\nPEEK\nPOP\nPOP\nISEMPTY\nSIZE",
         "3\n3\n5\nTrue\n0", False),
        ("3\nPOP\nPEEK\nISEMPTY",
         "Empty\nEmpty\nTrue", False),
        ("5\nPUSH 10\nPUSH 20\nSIZE\nPOP\nSIZE",
         "2\n20\n1", False),
        ("6\nPUSH 1\nPUSH 2\nPUSH 3\nPEEK\nPOP\nPEEK",
         "3\n3\n2", True),
        ("4\nPUSH -5\nPUSH 0\nPOP\nPOP",
         "0\n-5", True),
    ])

    # Exercise: Shape Hierarchy
    ex2 = _exercise(db, les3, "py-shape-hierarchy",
                    title="Shape Hierarchy",
                    difficulty=Difficulty.medium,
                    points=15,
                    time_limit_ms=3000,
                    memory_limit_mb=256,
                    is_published=True,
                    supported_languages=["python"],
                    prompt_md="""## Problem

Implement three shape classes that inherit from a base `Shape` class, each with `area()` and `perimeter()` methods.

**Shapes:**
- `Circle r` — area = π×r², perimeter = 2×π×r
- `Rectangle w h` — area = w×h, perimeter = 2×(w+h)
- `Triangle a b c` — Heron's formula for area; perimeter = a+b+c

## Input Format

- Line 1: integer N (number of shapes)
- Next N lines: shape type followed by dimensions

## Output Format

For each shape, print:
```
Area: X.XX Perimeter: Y.YY
```

Round to **2 decimal places**.

## Example

**Input**
```
3
Circle 5
Rectangle 4 6
Triangle 3 4 5
```

**Output**
```
Area: 78.54 Perimeter: 31.42
Area: 24.00 Perimeter: 20.00
Area: 6.00 Perimeter: 12.00
```

## Constraints

- 1 ≤ N ≤ 100
- All dimensions are positive floats.
""",
                    starter_code={"python": """import math
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...
    @abstractmethod
    def perimeter(self) -> float: ...

class Circle(Shape):
    def __init__(self, r):
        self.r = r
    # TODO: implement area() and perimeter()

class Rectangle(Shape):
    def __init__(self, w, h):
        self.w, self.h = w, h
    # TODO: implement area() and perimeter()

class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c
    # TODO: implement area() and perimeter() using Heron's formula

n = int(input())
for _ in range(n):
    parts = input().split()
    shape_type = parts[0]
    # TODO: create shape and print area + perimeter
"""},
                    solution_code={"python": """import math
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...
    @abstractmethod
    def perimeter(self) -> float: ...

class Circle(Shape):
    def __init__(self, r):
        self.r = float(r)
    def area(self):
        return math.pi * self.r ** 2
    def perimeter(self):
        return 2 * math.pi * self.r

class Rectangle(Shape):
    def __init__(self, w, h):
        self.w, self.h = float(w), float(h)
    def area(self):
        return self.w * self.h
    def perimeter(self):
        return 2 * (self.w + self.h)

class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a, self.b, self.c = float(a), float(b), float(c)
    def area(self):
        s = (self.a + self.b + self.c) / 2
        return math.sqrt(s * (s-self.a) * (s-self.b) * (s-self.c))
    def perimeter(self):
        return self.a + self.b + self.c

n = int(input())
for _ in range(n):
    parts = input().split()
    shape_type = parts[0]
    if shape_type == "Circle":
        shape = Circle(parts[1])
    elif shape_type == "Rectangle":
        shape = Rectangle(parts[1], parts[2])
    elif shape_type == "Triangle":
        shape = Triangle(parts[1], parts[2], parts[3])
    print(f"Area: {shape.area():.2f} Perimeter: {shape.perimeter():.2f}")
"""})
    _cases(db, ex2, [
        ("3\nCircle 5\nRectangle 4 6\nTriangle 3 4 5",
         "Area: 78.54 Perimeter: 31.42\nArea: 24.00 Perimeter: 20.00\nArea: 6.00 Perimeter: 12.00", False),
        ("1\nCircle 1",
         "Area: 3.14 Perimeter: 6.28", False),
        ("1\nRectangle 10 5",
         "Area: 50.00 Perimeter: 30.00", False),
        ("2\nTriangle 5 12 13\nCircle 7",
         "Area: 30.00 Perimeter: 30.00\nArea: 153.94 Perimeter: 43.98", True),
        ("1\nTriangle 6 8 10",
         "Area: 24.00 Perimeter: 24.00", True),
    ])


# ─────────────────────────────────────────────
# Module 7: Files, Exceptions, and Modules
# ─────────────────────────────────────────────

def _build_module7(db: Session, course: Course) -> None:
    mod = _module(db, course, "Files, Exceptions, and Modules", 7,
                  "Handle errors gracefully, read and write files, and leverage the standard library.")

    # Lesson 1 – Exception Handling (reading)
    _lesson(db, mod, "python-exceptions",
            title="Exception Handling",
            lesson_type=LessonType.reading,
            duration_minutes=18,
            order_index=1,
            content_md="""# Exception Handling

## try / except / else / finally

```python
try:
    result = int(input("Enter a number: "))
except ValueError as e:
    print(f"Invalid input: {e}")
except (TypeError, OverflowError):
    print("Type or overflow error")
else:
    print(f"You entered: {result}")   # runs only if no exception
finally:
    print("This always runs")          # cleanup: close files, etc.
```

- `except Exception` catches most exceptions; avoid bare `except:` (catches `SystemExit` and `KeyboardInterrupt` too).
- Use specific exception types whenever you know what to expect.

## Exception Hierarchy (Simplified)

```
BaseException
├── SystemExit
├── KeyboardInterrupt
└── Exception
    ├── ArithmeticError
    │   ├── ZeroDivisionError
    │   └── OverflowError
    ├── LookupError
    │   ├── IndexError
    │   └── KeyError
    ├── TypeError
    ├── ValueError
    ├── IOError / OSError
    └── RuntimeError
```

## Raising Exceptions

```python
def divide(a, b):
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b

# Re-raise with context:
try:
    result = divide(10, 0)
except ZeroDivisionError as e:
    raise RuntimeError("Computation failed") from e
```

## Custom Exceptions

```python
class InsufficientFundsError(ValueError):
    def __init__(self, amount, balance):
        self.amount = amount
        self.balance = balance
        super().__init__(f"Cannot withdraw {amount}; balance is {balance}")

raise InsufficientFundsError(100, 50)
```

## Context Managers and the with Statement

```python
# Manual approach — error-prone:
f = open("data.txt")
data = f.read()
f.close()   # might not run if read() raises!

# Safe approach with with:
with open("data.txt") as f:
    data = f.read()
# f is automatically closed here
```

### Custom Context Manager

```python
from contextlib import contextmanager

@contextmanager
def managed_resource():
    print("Acquiring resource")
    try:
        yield "resource_handle"
    finally:
        print("Releasing resource")

with managed_resource() as res:
    print(f"Using {res}")
```

## Common Built-in Exceptions

| Exception | When it occurs |
|---|---|
| `ValueError` | Correct type, wrong value (`int("abc")`) |
| `TypeError` | Wrong type (`"a" + 1`) |
| `KeyError` | Missing dict key |
| `IndexError` | List index out of range |
| `AttributeError` | Attribute doesn't exist |
| `FileNotFoundError` | File doesn't exist |
| `ZeroDivisionError` | Division by zero |
""")

    # Lesson 2 – File I/O and Standard Library (reading)
    _lesson(db, mod, "python-files-io",
            title="File I/O and the Standard Library",
            lesson_type=LessonType.reading,
            duration_minutes=15,
            order_index=2,
            content_md="""# File I/O and the Standard Library

## Opening and Reading Files

```python
# Text mode (default)
with open("data.txt", "r", encoding="utf-8") as f:
    content = f.read()        # entire file as string
    lines   = f.readlines()   # list of lines (with \\n)

# Iterate line by line (memory-efficient):
with open("data.txt") as f:
    for line in f:
        print(line.rstrip())
```

### File Modes

| Mode | Meaning |
|---|---|
| `r` | Read (default) |
| `w` | Write (overwrites) |
| `a` | Append |
| `x` | Exclusive create (fails if exists) |
| `b` | Binary flag (`rb`, `wb`) |

## Writing Files

```python
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Line 1\\n")
    f.writelines(["Line 2\\n", "Line 3\\n"])
```

## pathlib — Modern Path Handling

```python
from pathlib import Path

p = Path("/home/user/data/file.txt")
p.exists()        # True/False
p.stem            # "file"
p.suffix          # ".txt"
p.parent          # Path("/home/user/data")
p.read_text()     # equivalent to open().read()
p.write_text("hello")

# Iterate a directory:
for child in Path(".").iterdir():
    print(child)
```

## json Module

```python
import json

# Serialise Python → JSON string
data = {"name": "Alice", "scores": [95, 87, 100]}
json_str = json.dumps(data, indent=2)

# Deserialise JSON string → Python
obj = json.loads(json_str)

# Read/write JSON files
with open("config.json") as f:
    config = json.load(f)

with open("output.json", "w") as f:
    json.dump(data, f, indent=2)
```

## datetime Module

```python
from datetime import date, datetime, timedelta

today = date.today()
now   = datetime.now()
delta = timedelta(days=7)
next_week = today + delta
print(now.strftime("%Y-%m-%d %H:%M"))
```

## random Module

```python
import random
random.randint(1, 6)         # random integer [1, 6]
random.choice([1,2,3,4,5])   # random element
random.shuffle(my_list)      # in-place shuffle
random.sample(range(100), 5) # 5 unique samples
random.seed(42)              # reproducible results
```

## itertools and functools (Overview)

```python
import itertools
list(itertools.chain([1,2], [3,4]))      # [1,2,3,4]
list(itertools.combinations([1,2,3], 2)) # [(1,2),(1,3),(2,3)]
list(itertools.permutations("AB"))       # [('A','B'),('B','A')]
list(itertools.islice(itertools.count(), 5))  # [0,1,2,3,4]
```

The standard library is vast — whenever you need something common, check `import` before writing it yourself.
""")

    # Lesson 3 – I/O and Exceptions Exercises (exercise)
    les3 = _lesson(db, mod, "python-io-exercises",
                   title="I/O and Exceptions Exercises",
                   lesson_type=LessonType.exercise,
                   duration_minutes=20,
                   order_index=3,
                   content_md="Practice robust error handling and JSON processing.")

    # Exercise: Safe Division
    ex1 = _exercise(db, les3, "py-safe-division",
                    title="Safe Division",
                    difficulty=Difficulty.easy,
                    points=10,
                    time_limit_ms=3000,
                    memory_limit_mb=256,
                    is_published=True,
                    supported_languages=["python"],
                    prompt_md="""## Problem

Read N pairs of values and for each pair compute `a / b`. Handle errors gracefully.

## Input Format

- Line 1: integer N
- Next N lines: two space-separated values `a b`

## Output Format

For each pair, print:
- The result formatted to **4 decimal places** if division succeeds
- `ZeroDivisionError` if b is 0
- `ValueError: not a number` if either value cannot be converted to float

## Example

**Input**
```
4
10 2
5 0
abc 3
9 3
```

**Output**
```
5.0000
ZeroDivisionError
ValueError: not a number
3.0000
```

## Constraints

- 1 ≤ N ≤ 100
""",
                    starter_code={"python": """n = int(input())
for _ in range(n):
    parts = input().split()
    # TODO: try to divide parts[0] / parts[1], handle errors
"""},
                    solution_code={"python": """n = int(input())
for _ in range(n):
    parts = input().split()
    try:
        a = float(parts[0])
        b = float(parts[1])
        if b == 0:
            raise ZeroDivisionError
        print(f"{a / b:.4f}")
    except ZeroDivisionError:
        print("ZeroDivisionError")
    except ValueError:
        print("ValueError: not a number")
"""})
    _cases(db, ex1, [
        ("4\n10 2\n5 0\nabc 3\n9 3",
         "5.0000\nZeroDivisionError\nValueError: not a number\n3.0000", False),
        ("2\n7 2\n1 0",
         "3.5000\nZeroDivisionError", False),
        ("1\n0 5",
         "0.0000", False),
        ("3\nhello world\n10 4\n0 0",
         "ValueError: not a number\n2.5000\nZeroDivisionError", True),
        ("2\n-9 3\n6 2",
         "-3.0000\n3.0000", True),
    ])

    # Exercise: JSON Processor
    ex2 = _exercise(db, les3, "py-json-processor",
                    title="JSON Key-Value Processor",
                    difficulty=Difficulty.medium,
                    points=15,
                    time_limit_ms=3000,
                    memory_limit_mb=256,
                    is_published=True,
                    supported_languages=["python"],
                    prompt_md="""## Problem

Read a JSON string from the first line, then process commands against it.

**Commands:**
- `GET key` — print the value for key, or `"Key not found"` if missing
- `SET key value` — set key to value (treated as a string), print `"OK"`
- `DELETE key` — delete key if present and print `"Deleted"`, else `"Key not found"`
- `KEYS` — print all keys sorted alphabetically, space-separated (or `"No keys"` if empty)

If the first line is not valid JSON, print `"Invalid JSON"` and stop.

## Input Format

- Line 1: a JSON object string
- Line 2: integer N
- Next N lines: commands

## Output Format

One line of output per command.

## Example

**Input**
```
{"name": "Alice", "age": "30"}
4
GET name
SET city Cairo
KEYS
DELETE age
```

**Output**
```
Alice
OK
age city name
Deleted
```

## Constraints

- 1 ≤ N ≤ 50
- Keys and values are strings.
""",
                    starter_code={"python": """import json

raw = input()
try:
    data = json.loads(raw)
except json.JSONDecodeError:
    print("Invalid JSON")
    import sys; sys.exit(0)

n = int(input())
for _ in range(n):
    cmd = input().split(maxsplit=2)
    # TODO: process GET, SET, DELETE, KEYS commands
"""},
                    solution_code={"python": """import json
import sys

raw = input()
try:
    data = json.loads(raw)
except json.JSONDecodeError:
    print("Invalid JSON")
    sys.exit(0)

n = int(input())
for _ in range(n):
    parts = input().split(maxsplit=2)
    cmd = parts[0]
    if cmd == "GET":
        key = parts[1]
        print(data.get(key, "Key not found"))
    elif cmd == "SET":
        key, value = parts[1], parts[2]
        data[key] = value
        print("OK")
    elif cmd == "DELETE":
        key = parts[1]
        if key in data:
            del data[key]
            print("Deleted")
        else:
            print("Key not found")
    elif cmd == "KEYS":
        keys = sorted(data.keys())
        print(" ".join(keys) if keys else "No keys")
"""})
    _cases(db, ex2, [
        ('{"name": "Alice", "age": "30"}\n4\nGET name\nSET city Cairo\nKEYS\nDELETE age',
         "Alice\nOK\nage city name\nDeleted", False),
        ('{"x": "1"}\n2\nDELETE x\nKEYS',
         "Deleted\nNo keys", False),
        ('not-json\n1\nGET key',
         "Invalid JSON", False),
        ('{}\n3\nGET missing\nSET a b\nKEYS',
         "Key not found\nOK\na", True),
        ('{"z": "26", "a": "1"}\n2\nKEYS\nDELETE missing',
         "a z\nKey not found", True),
    ])


# ─────────────────────────────────────────────
# Module 8: Pythonic Code and Best Practices
# ─────────────────────────────────────────────

def _build_module8(db: Session, course: Course) -> None:
    mod = _module(db, course, "Pythonic Code and Best Practices", 8,
                  "Write clean, efficient, idiomatic Python using the community's best patterns.")

    # Lesson 1 – Pythonic Patterns (reading)
    _lesson(db, mod, "python-idioms",
            title="Pythonic Patterns",
            lesson_type=LessonType.reading,
            duration_minutes=18,
            order_index=1,
            content_md="""# Pythonic Patterns

## What Does "Pythonic" Mean?

Pythonic code follows the conventions and idioms that experienced Python developers consider natural and readable. It usually means shorter, clearer code that leverages Python's features rather than fighting them.

## PEP 8 Highlights

- 4-space indentation
- Maximum line length 79 characters (79–99 is acceptable in modern projects)
- Two blank lines between top-level definitions
- One blank line between methods in a class
- Imports at the top: stdlib → third-party → local
- `snake_case` for variables/functions, `PascalCase` for classes, `UPPER_CASE` for constants

## Comprehensions vs Explicit Loops

```python
# Not Pythonic
result = []
for x in range(10):
    if x % 2 == 0:
        result.append(x ** 2)

# Pythonic
result = [x**2 for x in range(10) if x % 2 == 0]
```

Dict and set comprehensions work the same way:

```python
word_lengths = {word: len(word) for word in sentence.split()}
unique_chars  = {ch.lower() for ch in text if ch.isalpha()}
```

## Generator Expressions for Memory Efficiency

```python
# Creates the entire list in memory:
total = sum([x**2 for x in range(10**6)])

# Generator expression — lazy, O(1) memory:
total = sum(x**2 for x in range(10**6))
```

## Unpacking Idioms

```python
# Swap without temp variable
a, b = b, a

# Ignore values with _
first, *_, last = [1, 2, 3, 4, 5]

# Unpack in for loop
pairs = [(1, 'a'), (2, 'b')]
for num, letter in pairs:
    print(num, letter)
```

## enumerate() and zip() — No More range(len())

```python
# Not Pythonic
for i in range(len(items)):
    print(i, items[i])

# Pythonic
for i, item in enumerate(items):
    print(i, item)

# Parallel iteration
for a, b in zip(list1, list2):
    print(a, b)
```

## Safe Dict Access

```python
# Risky
value = d["key"]         # raises KeyError if missing

# Safe options
value = d.get("key", default_value)
value = d.setdefault("key", default_value)  # also inserts

# For counting patterns
from collections import defaultdict
counts = defaultdict(int)
```

## any() and all()

```python
numbers = [1, 2, 3, 4, 5]
any(n > 4 for n in numbers)   # True  — any n > 4?
all(n > 0 for n in numbers)   # True  — all positive?
```

## Walrus Operator and f-string Tricks

```python
# Process chunks of a stream
while chunk := f.read(8192):
    process(chunk)

# f-string alignment and format
print(f"{'Name':<15} {'Score':>5}")
pi = 3.14159
print(f"{pi:.2f}")      # "3.14"
print(f"{pi!r}")        # repr(pi)
print(f"{1_000_000:,}") # "1,000,000"
```
""")

    # Lesson 2 – Performance and Tooling (reading)
    _lesson(db, mod, "python-performance",
            title="Performance and Tooling",
            lesson_type=LessonType.reading,
            duration_minutes=15,
            order_index=2,
            content_md="""# Performance and Tooling

## Profiling Your Code

Before optimising, **measure**:

```python
import cProfile
cProfile.run("my_function()")

import timeit
timeit.timeit("sorted([3,1,2])", number=100_000)
```

Use `line_profiler` for line-by-line analysis of hot functions.

## Big-O of Built-in Operations

| Operation | Time Complexity |
|---|---|
| `list.append(x)` | O(1) amortised |
| `list.insert(0, x)` | O(n) |
| `list[i]` | O(1) |
| `x in list` | O(n) |
| `x in set` / `x in dict` | O(1) average |
| `dict[key]` | O(1) average |
| `list.sort()` | O(n log n) |
| `min(list)` / `max(list)` | O(n) |

**Key insight:** If you need fast membership testing, use a `set` or `dict`, not a `list`.

## Generators for Large Data

```python
# Reads entire file into RAM:
lines = open("huge.txt").readlines()

# Lazy — reads one line at a time:
def read_lines(path):
    with open(path) as f:
        for line in f:
            yield line.rstrip()

for line in read_lines("huge.txt"):
    process(line)
```

Generators are also more composable — you can chain them in pipelines.

## Virtual Environments

Always isolate project dependencies:

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\\Scripts\\activate         # Windows
pip install requests fastapi
pip freeze > requirements.txt
```

## Package Management with pip

```bash
pip install package_name
pip install package_name==1.2.3   # pin version
pip install -r requirements.txt
pip list --outdated
pip show package_name
```

## Code Quality Tools

| Tool | Purpose |
|---|---|
| `black` | Opinionated auto-formatter |
| `ruff` | Very fast linter (replaces flake8, isort) |
| `flake8` | Style and error linter |
| `mypy` | Static type checker |
| `pytest` | Test framework |

Run before every commit:

```bash
black .
ruff check .
mypy src/
pytest
```

## The array Module and NumPy

For numeric-intensive code:

```python
import array
a = array.array('d', [1.0, 2.0, 3.0])  # typed, more memory-efficient than list

import numpy as np
arr = np.array([1, 2, 3, 4])
arr * 2          # [2, 4, 6, 8] — vectorised, very fast
arr.mean()       # 2.5
```

NumPy is the foundation of the entire Python data-science ecosystem.
""")

    # Lesson 3 – Advanced Python Exercises (exercise)
    les3 = _lesson(db, mod, "python-advanced-exercises",
                   title="Advanced Python Exercises",
                   lesson_type=LessonType.exercise,
                   duration_minutes=25,
                   order_index=3,
                   content_md="Test your mastery of generators, pipelines, and simulation.")

    # Exercise: Generator Pipeline
    ex1 = _exercise(db, les3, "py-generator-pipeline",
                    title="Generator Pipeline",
                    difficulty=Difficulty.medium,
                    points=15,
                    time_limit_ms=3000,
                    memory_limit_mb=256,
                    is_published=True,
                    supported_languages=["python"],
                    prompt_md="""## Problem

Implement a data-processing pipeline using generators:

1. **Source**: read N integers from the first line
2. **Filter**: keep only even numbers
3. **Transform**: square each remaining number
4. **Take**: take the first K values from the transformed stream
5. **Reduce**: sum those K values

The command line tells you what to do:
- `FILTER_EVEN` — filter evens
- `SQUARE` — square values
- `TAKE K` — take first K
- `SUM` — compute and print the sum

The pipeline is always in this fixed order: FILTER_EVEN → SQUARE → TAKE K → SUM.

## Input Format

- Line 1: N space-separated integers
- Line 2: the command string (always `FILTER_EVEN SQUARE TAKE K SUM`)

## Output Format

A single integer: the final sum.

## Example

**Input**
```
1 2 3 4 5 6 7 8 9 10
FILTER_EVEN SQUARE TAKE 3 SUM
```

**Output**
```
56
```

Explanation: evens = [2,4,6,8,10], squared = [4,16,36,64,100], take 3 = [4,16,36], sum = 56.

## Constraints

- 1 ≤ N ≤ 10000
- 1 ≤ K ≤ N
""",
                    starter_code={"python": """import itertools

nums = list(map(int, input().split()))
cmd_line = input().split()
# Parse K from cmd_line
k = int(cmd_line[cmd_line.index("TAKE") + 1])

# TODO: build pipeline using generators and print sum
"""},
                    solution_code={"python": """import itertools

nums = list(map(int, input().split()))
cmd_line = input().split()
k = int(cmd_line[cmd_line.index("TAKE") + 1])

def filter_even(source):
    for x in source:
        if x % 2 == 0:
            yield x

def square(source):
    for x in source:
        yield x * x

pipeline = itertools.islice(square(filter_even(nums)), k)
print(sum(pipeline))
"""})
    _cases(db, ex1, [
        ("1 2 3 4 5 6 7 8 9 10\nFILTER_EVEN SQUARE TAKE 3 SUM",
         "56", False),
        ("2 4 6 8\nFILTER_EVEN SQUARE TAKE 4 SUM",
         "120", False),
        ("1 3 5 7\nFILTER_EVEN SQUARE TAKE 1 SUM",
         "0", False),
        ("10 20 30 40 50\nFILTER_EVEN SQUARE TAKE 2 SUM",
         "500", True),
        ("0 2 4 6 8 10\nFILTER_EVEN SQUARE TAKE 5 SUM",
         "220", True),
    ])

    # Exercise: Decorator Timer Simulation
    ex2 = _exercise(db, les3, "py-decorator-timer",
                    title="Retry Call Log Simulator",
                    difficulty=Difficulty.medium,
                    points=15,
                    time_limit_ms=3000,
                    memory_limit_mb=256,
                    is_published=True,
                    supported_languages=["python"],
                    prompt_md="""## Problem

Simulate a retry decorator. You are given a log of function calls, each with an execution time. A call is considered a **failure** if its execution time exceeds a threshold T. If it fails, retry up to R more times (reading subsequent log entries for the same function). Report the outcome.

## Input Format

- Line 1: integers `T R` — threshold (ms) and max retries
- Line 2: integer N — number of log entries
- Next N lines: `function_name execution_time_ms`

Process calls in order. When you encounter a function call:
- If execution_time ≤ T: SUCCESS (use remaining log entries for next functions)
- If execution_time > T and retries remain: retry (consume next log entry for the same function)
- If all retries exhausted: FAIL

## Output Format

For each distinct function call group, print:
```
function_name attempts_used SUCCESS
```
or
```
function_name attempts_used FAIL
```

## Example

**Input**
```
100 2
5
api_call 50
api_call 200
api_call 80
db_query 150
db_query 120
```

**Output**
```
api_call 1 SUCCESS
api_call 3 SUCCESS
db_query 2 FAIL
```

Wait — let me re-read. Each group starts fresh. Entries are consumed sequentially, one group at a time (1 attempt + up to R retries).

Re-explanation: consume entries in order. First call uses entry 1. If fail, retry with entry 2, etc. Next distinct call group starts after the previous group finished.

## Constraints

- 1 ≤ T ≤ 10000, 1 ≤ R ≤ 10
- 1 ≤ N ≤ 100
""",
                    starter_code={"python": """import sys

line1 = input().split()
T, R = int(line1[0]), int(line1[1])
n = int(input())
entries = []
for _ in range(n):
    parts = input().split()
    entries.append((parts[0], int(parts[1])))

i = 0
while i < len(entries):
    func_name, time_ms = entries[i]
    attempts = 1
    # TODO: simulate retry logic and print result
    i += 1
"""},
                    solution_code={"python": """line1 = input().split()
T, R = int(line1[0]), int(line1[1])
n = int(input())
entries = []
for _ in range(n):
    parts = input().split()
    entries.append((parts[0], int(parts[1])))

i = 0
while i < len(entries):
    func_name, time_ms = entries[i]
    attempts = 1
    if time_ms <= T:
        print(f"{func_name} {attempts} SUCCESS")
        i += 1
        continue
    # Failed — try retries
    success = False
    retries_used = 0
    while retries_used < R and (i + 1) < len(entries):
        i += 1
        retries_used += 1
        attempts += 1
        _, next_time = entries[i]
        if next_time <= T:
            success = True
            break
    outcome = "SUCCESS" if success else "FAIL"
    print(f"{func_name} {attempts} {outcome}")
    i += 1
"""})
    _cases(db, ex2, [
        ("100 2\n5\napi_call 50\napi_call 200\napi_call 80\ndb_query 150\ndb_query 120",
         "api_call 1 SUCCESS\napi_call 3 SUCCESS\ndb_query 2 FAIL", False),
        ("50 1\n2\nfoo 60\nfoo 40",
         "foo 2 SUCCESS", False),
        ("100 3\n2\nbar 200\nbar 300",
         "bar 2 FAIL", False),
        ("200 2\n3\nping 100\npong 300\npong 150",
         "ping 1 SUCCESS\npong 2 SUCCESS", True),
        ("10 1\n4\nalpha 5\nbeta 20\nbeta 15\ngamma 8",
         "alpha 1 SUCCESS\nbeta 2 FAIL\ngamma 1 SUCCESS", True),
    ])


# ─────────────────────────────────────────────
# Main seed function
# ─────────────────────────────────────────────

def seed() -> None:
    print("Creating database tables if not present...")
    Base.metadata.create_all(bind=engine)

    print("Seeding Python Programming Fundamentals course...")
    with SessionLocal() as db:
        # 1. Subject
        subject = _ensure_subject(
            db,
            slug="programming-languages",
            name="Programming Languages",
            description="Courses covering programming languages and their core concepts, syntax, and idioms.",
            icon="code",
            color="#8b5cf6",
            order_index=4,
        )
        print(f"  Subject: {subject.name} (id={subject.id})")

        # 2. Course
        course = _ensure_course(
            db,
            subject,
            slug="python-fundamentals",
            title="Python Programming Fundamentals",
            summary="Learn Python from the ground up — syntax, data structures, OOP, and Pythonic patterns.",
            description=(
                "A comprehensive beginner course covering Python 3 from first principles. "
                "You will write working programs from day one and progressively build towards "
                "object-oriented design, the standard library, and idiomatic Python. "
                "Each module combines reading lessons with hands-on exercises graded automatically."
            ),
            difficulty="beginner",
            estimated_hours=20,
            is_published=True,
            order_index=1,
        )
        print(f"  Course: {course.title} (id={course.id})")

        # 3. Build all 8 modules
        _build_module1(db, course)
        print("  Module 1 done: Getting Started with Python")

        _build_module2(db, course)
        print("  Module 2 done: Data Types and Variables")

        _build_module3(db, course)
        print("  Module 3 done: Control Flow")

        _build_module4(db, course)
        print("  Module 4 done: Functions")

        _build_module5(db, course)
        print("  Module 5 done: Lists, Tuples, and Dictionaries")

        _build_module6(db, course)
        print("  Module 6 done: Object-Oriented Programming")

        _build_module7(db, course)
        print("  Module 7 done: Files, Exceptions, and Modules")

        _build_module8(db, course)
        print("  Module 8 done: Pythonic Code and Best Practices")

        db.commit()

    print("\nSeed complete.")
    print("  Subject : Programming Languages")
    print("  Course  : Python Programming Fundamentals")
    print("  Modules : 8")
    print("  Lessons : 24  (16 reading, 8 exercise)")
    print("  Exercises: 16")
    print("  Test cases: 80")


if __name__ == "__main__":
    seed()
