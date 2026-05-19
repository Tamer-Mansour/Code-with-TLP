"""
Full seed for "Introduction to Algorithms" course (MIT 6.006 / CLRS 4th ed.).
12 modules · 36 lessons · 30 exercises · 120+ test cases.

Run from the backend/ directory:
    python seed/intro_algorithms_seed.py
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine
from app.models import (
    Base,
    Course,
    Difficulty,
    Exercise,
    Lesson,
    LessonType,
    Module,
    Subject,
    Tag,
    TestCase,
)

LANGS = ["python", "javascript", "typescript", "java", "csharp"]


# ─────────────────────────────────────────────
# Idempotent helpers
# ─────────────────────────────────────────────

def _subject(db: Session, slug: str, **kw) -> Subject:
    obj = db.scalar(select(Subject).where(Subject.slug == slug))
    if not obj:
        obj = Subject(slug=slug, **kw)
        db.add(obj)
        db.flush()
    return obj


def _course(db: Session, subject: Subject, slug: str, **kw) -> Course:
    obj = db.scalar(select(Course).where(Course.slug == slug))
    if not obj:
        obj = Course(subject_id=subject.id, slug=slug, **kw)
        db.add(obj)
        db.flush()
    return obj


def _module(db: Session, course: Course, title: str, order: int, summary: str = "") -> Module:
    obj = db.scalar(select(Module).where(Module.course_id == course.id, Module.title == title))
    if not obj:
        obj = Module(course_id=course.id, title=title, order_index=order, summary=summary)
        db.add(obj)
        db.flush()
    return obj


def _lesson(db: Session, mod: Module, slug: str, **kw) -> Lesson:
    obj = db.scalar(select(Lesson).where(Lesson.module_id == mod.id, Lesson.slug == slug))
    if not obj:
        obj = Lesson(module_id=mod.id, slug=slug, **kw)
        db.add(obj)
        db.flush()
    return obj


def _exercise(db: Session, lesson: Lesson, slug: str, **kw) -> tuple[Exercise, bool]:
    obj = db.scalar(select(Exercise).where(Exercise.slug == slug))
    if not obj:
        obj = Exercise(lesson_id=lesson.id, slug=slug, **kw)
        db.add(obj)
        db.flush()
        return obj, True
    return obj, False


def _tag(db: Session, name: str, slug: str) -> Tag:
    obj = db.scalar(select(Tag).where(Tag.slug == slug))
    if not obj:
        obj = Tag(name=name, slug=slug)
        db.add(obj)
        db.flush()
    return obj


def _cases(db: Session, ex: Exercise, cases: list) -> None:
    """Add (name, stdin, expected, hidden, weight) tuples if exercise is new."""
    if ex.test_cases:
        return
    for i, (name, stdin, expected, hidden, weight) in enumerate(cases):
        db.add(TestCase(
            exercise_id=ex.id,
            name=name,
            stdin=stdin,
            expected_stdout=expected,
            is_hidden=hidden,
            weight=weight,
            order_index=i,
        ))


# ─────────────────────────────────────────────
# Reusable read-helpers for starters
# ─────────────────────────────────────────────

def py_read_n_array():
    return "import sys\ndata = sys.stdin.read().split()\nn = int(data[0])\na = list(map(int, data[1:n+1]))\n"

def js_read_lines():
    return ("const lines = require('fs').readFileSync(0,'utf8').trim().split('\\n');\n"
            "let li = 0;\n")

def ts_read_lines():
    return ("import * as fs from 'fs';\n"
            "const lines = fs.readFileSync(0,'utf8').trim().split('\\n');\n"
            "let li = 0;\n")

def java_scanner():
    return ("import java.util.*;\npublic class Main {\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n")

def java_end():
    return "    }\n}\n"

def cs_read():
    return ("using System;\nusing System.Linq;\nclass Solution {\n"
            "    static void Main() {\n")

def cs_end():
    return "    }\n}\n"


# ════════════════════════════════════════════════════════════════
#  MODULE 1 — Getting Started
# ════════════════════════════════════════════════════════════════

M1_INTRO_MD = """\
# What Is an Algorithm?

An **algorithm** is a finite, well-defined sequence of steps that takes some input
and produces output that solves a problem.

## Three key properties
1. **Correctness** — for every valid input the algorithm produces the right answer.
2. **Termination** — the algorithm always stops in a finite number of steps.
3. **Efficiency** — it uses as few resources (time, memory) as possible.

## A simple example: finding the maximum
```
max_val = a[0]
for each element x in a:
    if x > max_val:
        max_val = x
return max_val
```
This is correct (examines every element), terminates (finite loop), and runs in
**O(n)** time — we can't do better, since we must inspect every element at least once.

## Why algorithms matter
A bad algorithm can make a fast computer *slower* than a good algorithm on an
old one.  Sorting 10⁶ numbers:
- Bubble Sort: ≈ 10¹² operations — hours
- Merge Sort:  ≈ 2×10⁷  operations — milliseconds
"""

M1_RECURSION_MD = """\
# Recursion and Induction

Recursive algorithms solve a problem by reducing it to a *smaller instance* of
the same problem.

## Factorial — the classic example
```
fact(0) = 1                   # base case
fact(n) = n × fact(n-1)       # recursive case
```
**Correctness** is proved by *mathematical induction* — the same structure as
the recursion itself.

## Anatomy of a recursive function
1. **Base case** — smallest input solved directly (prevents infinite recursion).
2. **Recursive case** — reduces problem size and calls itself.
3. **Progress** — each call must move toward the base case.

## Call-stack depth
Every recursive call consumes stack space.  `fact(n)` has call-stack depth *n*.
For large *n* this causes a **stack overflow** — convert to iteration or use
tail-call optimisation.

## Divide-and-Conquer preview
Merge Sort divides the array in half each time:
```
sort([5,2,4,1,3]) → sort([5,2]) + sort([4,1,3]) → merge(...)
```
Depth = log₂ n, work per level = n → total O(n log n).
"""

M1_EXERCISE_MD = "Warm-up coding exercises to get started with algorithm implementation."


def seed_module1(db: Session, course: Course) -> None:
    mod = _module(db, course, "Getting Started", 1,
                  "What algorithms are, why they matter, and recursion basics.")

    _lesson(db, mod, "what-is-an-algorithm",
            title="What Is an Algorithm?",
            lesson_type=LessonType.reading,
            content_md=M1_INTRO_MD,
            duration_minutes=10,
            order_index=1)

    _lesson(db, mod, "recursion-and-induction",
            title="Recursion and Induction",
            lesson_type=LessonType.reading,
            content_md=M1_RECURSION_MD,
            duration_minutes=12,
            order_index=2)

    ex_lesson = _lesson(db, mod, "getting-started-exercises",
                        title="Getting Started — Exercises",
                        lesson_type=LessonType.exercise,
                        content_md=M1_EXERCISE_MD,
                        duration_minutes=20,
                        order_index=3)

    # ── Exercise 1.1: Factorial ──────────────────────────────────
    ex, new = _exercise(db, ex_lesson, "factorial",
        title="Factorial",
        prompt_md=(
            "# Factorial\n\n"
            "Given a non-negative integer **n**, compute and print **n!**\n\n"
            "Recall: 0! = 1, n! = n × (n−1)!\n\n"
            "**Input:** a single integer n (0 ≤ n ≤ 12)\n\n"
            "**Output:** n!\n\n"
            "**Example**\n```\nInput:  5\nOutput: 120\n```"
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def factorial(n: int) -> int:\n"
                "    # TODO: implement using recursion or iteration\n"
                "    pass\n\n"
                "n = int(sys.stdin.read().strip())\n"
                "print(factorial(n))\n"
            ),
            "javascript": (
                "const n = parseInt(require('fs').readFileSync(0,'utf8').trim());\n\n"
                "function factorial(n) {\n"
                "    // TODO\n"
                "}\n\n"
                "console.log(factorial(n));\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const n = parseInt(fs.readFileSync(0,'utf8').trim());\n\n"
                "function factorial(n: number): number {\n"
                "    // TODO\n"
                "    return 0;\n"
                "}\n\n"
                "console.log(factorial(n));\n"
            ),
            "java": (
                "import java.util.Scanner;\n"
                "public class Main {\n"
                "    static long factorial(int n) {\n"
                "        // TODO\n"
                "        return 0;\n"
                "    }\n"
                "    public static void main(String[] args) {\n"
                "        Scanner sc = new Scanner(System.in);\n"
                "        System.out.println(factorial(sc.nextInt()));\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\n"
                "class Solution {\n"
                "    static long Factorial(int n) {\n"
                "        // TODO\n"
                "        return 0;\n"
                "    }\n"
                "    static void Main() {\n"
                "        Console.WriteLine(Factorial(int.Parse(Console.ReadLine().Trim())));\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n\n"
                "def factorial(n):\n"
                "    if n <= 1: return 1\n"
                "    return n * factorial(n - 1)\n\n"
                "print(factorial(int(sys.stdin.read().strip())))\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=3000,
        memory_limit_mb=128,
        points=10,
    )
    _cases(db, ex, [
        ("zero",   "0\n",  "1",         False, 1),
        ("small",  "5\n",  "120",        False, 1),
        ("medium", "10\n", "3628800",    False, 1),
        ("large",  "12\n", "479001600",  True,  2),
    ])

    # ── Exercise 1.2: Array Sum ──────────────────────────────────
    ex, new = _exercise(db, ex_lesson, "array-sum",
        title="Array Sum",
        prompt_md=(
            "# Array Sum\n\n"
            "Read **n** integers and print their sum.\n\n"
            "**Input:**\n```\nn\na₁ a₂ … aₙ\n```\n\n"
            "**Output:** sum of all elements\n\n"
            "**Example**\n```\nInput:\n5\n1 2 3 4 5\n\nOutput:\n15\n```"
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "data = sys.stdin.read().split()\n"
                "n = int(data[0])\n"
                "a = list(map(int, data[1:n+1]))\n\n"
                "# TODO: print the sum of a\n"
            ),
            "javascript": (
                "const data = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n = data[0];\n"
                "const a = data.slice(1, n + 1);\n"
                "// TODO: print the sum\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const data = fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n = data[0];\n"
                "const a = data.slice(1, n + 1);\n"
                "// TODO: print the sum\n"
            ),
            "java": (
                "import java.util.Scanner;\n"
                "public class Main {\n"
                "    public static void main(String[] args) {\n"
                "        Scanner sc = new Scanner(System.in);\n"
                "        int n = sc.nextInt();\n"
                "        long sum = 0;\n"
                "        for (int i = 0; i < n; i++) sum += sc.nextLong();\n"
                "        // TODO: print sum\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Linq;\n"
                "class Solution {\n"
                "    static void Main() {\n"
                "        int n = int.Parse(Console.ReadLine().Trim());\n"
                "        var a = Console.ReadLine().Trim().Split().Select(long.Parse);\n"
                "        // TODO: print sum\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "d=sys.stdin.read().split()\n"
                "n=int(d[0])\n"
                "print(sum(map(int,d[1:n+1])))\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=3000,
        memory_limit_mb=128,
        points=10,
    )
    _cases(db, ex, [
        ("basic",    "5\n1 2 3 4 5\n",   "15",  False, 1),
        ("negatives","3\n-1 0 1\n",       "0",   False, 1),
        ("single",   "1\n42\n",           "42",  False, 1),
        ("large",    "4\n1000 2000 3000 4000\n", "10000", True, 2),
    ])


# ════════════════════════════════════════════════════════════════
#  MODULE 2 — Asymptotic Notation & Big-O
# ════════════════════════════════════════════════════════════════

M2_BIGO_MD = """\
# Asymptotic Notation

We analyse algorithms by how their running time **grows** with input size n.
We ignore constants and lower-order terms — they are hardware-dependent.

## Big-O (upper bound)
f(n) = O(g(n)) iff there exist c > 0 and n₀ such that f(n) ≤ c·g(n) for all n ≥ n₀.

Example: 3n² + 5n + 10 = O(n²)  (take c = 4, n₀ = 16)

## Big-Ω (lower bound)
f(n) = Ω(g(n)) iff g(n) = O(f(n)).

## Big-Θ (tight bound)
f(n) = Θ(g(n)) iff f(n) = O(g(n)) AND f(n) = Ω(g(n)).

## Common growth rates (slowest → fastest)
| Notation | Name |
|----------|------|
| O(1) | Constant |
| O(log n) | Logarithmic |
| O(√n) | Square root |
| O(n) | Linear |
| O(n log n) | Linearithmic |
| O(n²) | Quadratic |
| O(n³) | Cubic |
| O(2ⁿ) | Exponential |
| O(n!) | Factorial |

## Amortized analysis
Some operations are occasionally expensive.  **Amortized O(1)** means the
*average* cost over many operations is O(1), even if occasional ops cost O(n).
Dynamic-array `append` is amortized O(1) via the **doubling trick**.
"""

M2_MASTER_MD = """\
# Recurrences and the Master Theorem

Divide-and-conquer algorithms split a problem of size n into **a** subproblems
of size **n/b**, with extra work **f(n)** at each level.

Recurrence: **T(n) = aT(n/b) + f(n)**

## Master Theorem cases
Let c* = log_b(a).

| Case | Condition | Solution |
|------|-----------|----------|
| 1 | f(n) = O(n^(c*−ε)) | T(n) = Θ(n^c*) |
| 2 | f(n) = Θ(n^c*) | T(n) = Θ(n^c* log n) |
| 3 | f(n) = Ω(n^(c*+ε)) and regularity | T(n) = Θ(f(n)) |

## Classic examples
| Algorithm | Recurrence | Result |
|-----------|-----------|--------|
| Binary Search | T(n) = T(n/2) + O(1) | O(log n) |
| Merge Sort | T(n) = 2T(n/2) + O(n) | O(n log n) |
| Strassen | T(n) = 7T(n/2) + O(n²) | O(n^2.807) |
| Karatsuba | T(n) = 3T(n/2) + O(n) | O(n^1.585) |

## Substitution method (informal)
Guess a solution, verify by substituting back and choosing constants.
Recursion-tree method visualises cost at each level.
"""

M2_EXERCISE_MD = "Apply binary search and practice recognising time complexities."


def seed_module2(db: Session, course: Course) -> None:
    mod = _module(db, course, "Asymptotic Notation and Big-O", 2,
                  "Big-O, Omega, Theta notation and the Master Theorem.")

    _lesson(db, mod, "big-o-notation",
            title="Big-O, Omega, and Theta Notation",
            lesson_type=LessonType.reading,
            content_md=M2_BIGO_MD,
            duration_minutes=15,
            order_index=1)

    _lesson(db, mod, "master-theorem",
            title="Recurrences and the Master Theorem",
            lesson_type=LessonType.reading,
            content_md=M2_MASTER_MD,
            duration_minutes=15,
            order_index=2)

    ex_lesson = _lesson(db, mod, "big-o-exercises",
                        title="Asymptotic Notation — Exercises",
                        lesson_type=LessonType.exercise,
                        content_md=M2_EXERCISE_MD,
                        duration_minutes=25,
                        order_index=3)

    # ── Exercise 2.1: Binary Search ──────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "binary-search",
        title="Binary Search",
        prompt_md=(
            "# Binary Search\n\n"
            "Given a **sorted** array of n integers and a query value q,\n"
            "print the **0-based index** where q is found, or **-1** if absent.\n\n"
            "**Input:**\n```\nn\na₁ a₂ … aₙ  (sorted ascending)\nq\n```\n\n"
            "**Output:** index or -1\n\n"
            "**Example**\n```\nInput:\n7\n1 3 5 7 9 11 13\n7\n\nOutput:\n3\n```"
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def binary_search(a, q):\n"
                "    lo, hi = 0, len(a) - 1\n"
                "    while lo <= hi:\n"
                "        mid = (lo + hi) // 2\n"
                "        # TODO: compare a[mid] with q and update lo/hi\n"
                "        pass\n"
                "    return -1\n\n"
                "data = sys.stdin.read().split()\n"
                "n = int(data[0])\n"
                "a = list(map(int, data[1:n+1]))\n"
                "q = int(data[n+1])\n"
                "print(binary_search(a, q))\n"
            ),
            "javascript": (
                "const d = require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n = d[0], a = d.slice(1,n+1), q = d[n+1];\n\n"
                "function binarySearch(a, q) {\n"
                "    let lo = 0, hi = a.length - 1;\n"
                "    while (lo <= hi) {\n"
                "        const mid = (lo + hi) >> 1;\n"
                "        // TODO\n"
                "    }\n"
                "    return -1;\n"
                "}\n\n"
                "console.log(binarySearch(a, q));\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d = fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n = d[0], a = d.slice(1,n+1), q = d[n+1];\n\n"
                "function binarySearch(a: number[], q: number): number {\n"
                "    let lo = 0, hi = a.length - 1;\n"
                "    while (lo <= hi) {\n"
                "        const mid = (lo + hi) >> 1;\n"
                "        // TODO\n"
                "    }\n"
                "    return -1;\n"
                "}\n\n"
                "console.log(binarySearch(a, q));\n"
            ),
            "java": (
                "import java.util.Scanner;\n"
                "public class Main {\n"
                "    static int binarySearch(int[] a, int q) {\n"
                "        int lo = 0, hi = a.length - 1;\n"
                "        while (lo <= hi) {\n"
                "            int mid = (lo + hi) >>> 1;\n"
                "            // TODO\n"
                "        }\n"
                "        return -1;\n"
                "    }\n"
                "    public static void main(String[] args) {\n"
                "        Scanner sc = new Scanner(System.in);\n"
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i = 0; i < n; i++) a[i] = sc.nextInt();\n"
                "        System.out.println(binarySearch(a, sc.nextInt()));\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\n"
                "class Solution {\n"
                "    static int BinarySearch(int[] a, int q) {\n"
                "        int lo = 0, hi = a.Length - 1;\n"
                "        while (lo <= hi) {\n"
                "            int mid = (lo + hi) / 2;\n"
                "            // TODO\n"
                "        }\n"
                "        return -1;\n"
                "    }\n"
                "    static void Main() {\n"
                "        int n = int.Parse(Console.ReadLine().Trim());\n"
                "        var a = Array.ConvertAll(Console.ReadLine().Trim().Split(), int.Parse);\n"
                "        int q = int.Parse(Console.ReadLine().Trim());\n"
                "        Console.WriteLine(BinarySearch(a, q));\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "d=sys.stdin.read().split()\n"
                "n=int(d[0]);a=list(map(int,d[1:n+1]));q=int(d[n+1])\n"
                "lo,hi=0,n-1\n"
                "ans=-1\n"
                "while lo<=hi:\n"
                "    mid=(lo+hi)//2\n"
                "    if a[mid]==q: ans=mid; break\n"
                "    elif a[mid]<q: lo=mid+1\n"
                "    else: hi=mid-1\n"
                "print(ans)\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=3000,
        memory_limit_mb=128,
        points=15,
    )
    _cases(db, ex, [
        ("found-middle", "7\n1 3 5 7 9 11 13\n7\n",   "3",  False, 1),
        ("not-found",    "5\n2 4 6 8 10\n5\n",         "-1", False, 1),
        ("first-elem",   "6\n1 2 3 4 5 6\n1\n",        "0",  False, 1),
        ("last-elem",    "6\n1 2 3 4 5 6\n6\n",        "5",  True,  2),
        ("single-found", "1\n42\n42\n",                 "0",  True,  1),
        ("single-miss",  "1\n42\n7\n",                  "-1", True,  1),
    ])

    # ── Exercise 2.2: Maximum Subarray (Kadane's) ─────────────────
    ex, _ = _exercise(db, ex_lesson, "maximum-subarray-sum",
        title="Maximum Subarray Sum",
        prompt_md=(
            "# Maximum Subarray Sum\n\n"
            "Given an array of n integers (possibly negative), find the **maximum sum**\n"
            "of any contiguous subarray.  The subarray must contain at least one element.\n\n"
            "**Input:**\n```\nn\na₁ a₂ … aₙ\n```\n\n"
            "**Output:** maximum subarray sum\n\n"
            "**Example**\n```\nInput:\n8\n-2 1 -3 4 -1 2 1 -5\n\nOutput:\n6\n```\n\n"
            "*Hint: Kadane's algorithm runs in O(n).*"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def max_subarray(a):\n"
                "    # TODO: Kadane's algorithm\n"
                "    pass\n\n"
                "data = sys.stdin.read().split()\n"
                "n = int(data[0])\n"
                "a = list(map(int, data[1:n+1]))\n"
                "print(max_subarray(a))\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0], a=d.slice(1,n+1);\n\n"
                "function maxSubarray(a) {\n"
                "    // TODO: Kadane's algorithm\n"
                "}\n\n"
                "console.log(maxSubarray(a));\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0], a=d.slice(1,n+1);\n\n"
                "function maxSubarray(a: number[]): number {\n"
                "    // TODO\n"
                "    return 0;\n"
                "}\n\n"
                "console.log(maxSubarray(a));\n"
            ),
            "java": (
                "import java.util.Scanner;\n"
                "public class Main {\n"
                "    public static void main(String[] args) {\n"
                "        Scanner sc = new Scanner(System.in);\n"
                "        int n = sc.nextInt();\n"
                "        int[] a = new int[n];\n"
                "        for (int i=0;i<n;i++) a[i]=sc.nextInt();\n"
                "        // TODO: Kadane's\n"
                "        long best = a[0], cur = a[0];\n"
                "        System.out.println(best);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\n"
                "class Solution {\n"
                "    static void Main() {\n"
                "        int n = int.Parse(Console.ReadLine().Trim());\n"
                "        var a = Array.ConvertAll(Console.ReadLine().Trim().Split(), int.Parse);\n"
                "        // TODO: Kadane's\n"
                "        Console.WriteLine(a[0]);\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "d=sys.stdin.read().split()\n"
                "n=int(d[0]);a=list(map(int,d[1:n+1]))\n"
                "best=cur=a[0]\n"
                "for x in a[1:]:\n"
                "    cur=max(x,cur+x)\n"
                "    best=max(best,cur)\n"
                "print(best)\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=3000,
        memory_limit_mb=128,
        points=20,
    )
    _cases(db, ex, [
        ("mixed",    "8\n-2 1 -3 4 -1 2 1 -5\n",  "6",   False, 1),
        ("all-pos",  "5\n1 2 3 4 5\n",              "15",  False, 1),
        ("all-neg",  "4\n-3 -2 -1 -4\n",            "-1",  False, 1),
        ("single",   "1\n-7\n",                      "-7",  False, 1),
        ("hidden-1", "6\n-2 -1 2 3 -4 5\n",         "6",   True,  2),
        ("hidden-2", "5\n5 -3 5 -3 5\n",             "9",   True,  2),
    ])


# ════════════════════════════════════════════════════════════════
#  MODULE 3 — Sorting Algorithms
# ════════════════════════════════════════════════════════════════

M3_COMPARISON_MD = """\
# Comparison-Based Sorting

A **comparison sort** determines order solely by comparing pairs of elements.

## Lower bound: Ω(n log n)
Any comparison sort must make at least Ω(n log n) comparisons in the worst case.
*Proof sketch:* there are n! possible permutations; a binary decision tree needs
height ≥ log₂(n!) = Θ(n log n) by Stirling's approximation.

## Key algorithms

| Algorithm | Best | Average | Worst | Space | Stable |
|-----------|------|---------|-------|-------|--------|
| Insertion Sort | Ω(n) | Θ(n²) | O(n²) | O(1) | ✓ |
| Merge Sort | Ω(n log n) | Θ(n log n) | O(n log n) | O(n) | ✓ |
| Heap Sort | Ω(n log n) | Θ(n log n) | O(n log n) | O(1) | ✗ |
| Quicksort (rand.) | Ω(n log n) | Θ(n log n) | O(n²) | O(log n) | ✗ |

## Insertion Sort
Efficient for small or nearly-sorted arrays.  Each element is inserted into its
correct position among already-sorted elements.
```
for i in 1..n-1:
    key = a[i]
    j = i - 1
    while j >= 0 and a[j] > key:
        a[j+1] = a[j]; j -= 1
    a[j+1] = key
```

## Merge Sort
Divide-and-conquer: split, sort halves recursively, merge in O(n).
Guaranteed O(n log n) in all cases; stable; requires O(n) extra space.

## Quicksort
Partition around a pivot; expected O(n log n) with random pivot.
Fast in practice due to cache locality; not stable.
"""

M3_LINEAR_MD = """\
# Linear-Time Sorting

When inputs satisfy constraints (bounded integers, small range), we can
sort faster than Ω(n log n).

## Counting Sort — O(n + k)
Count occurrences of each value in range [0, k−1].
Works only for **integer keys** with known bounded range.
Stable — preserves relative order of equal keys.

```
count = [0] * (k + 1)
for x in a: count[x] += 1
# prefix-sum to get positions
for i in 1..k: count[i] += count[i-1]
# place elements (iterate right-to-left for stability)
```

## Radix Sort — O(d · (n + k))
Sort digit-by-digit using a stable sort (counting sort) as subroutine.
d = number of digits, k = base (usually 10 or 256).

## Bucket Sort — O(n) expected
Distribute elements into buckets; sort each bucket (usually insertion sort);
concatenate.  Optimal when input is uniformly distributed over [0, 1).

## When to use which
- Small integer keys with bounded range → Counting Sort
- Large integers with fixed width → Radix Sort
- Floating-point uniformly distributed → Bucket Sort
- General case (unknown distribution) → Merge / Quicksort
"""

M3_EXERCISE_MD = "Implement sorting algorithms from scratch and analyse inversion counts."


def seed_module3(db: Session, course: Course) -> None:
    mod = _module(db, course, "Sorting Algorithms", 3,
                  "Comparison sorts, linear-time sorts, and inversion counting.")

    _lesson(db, mod, "comparison-sorting",
            title="Comparison-Based Sorting",
            lesson_type=LessonType.reading,
            content_md=M3_COMPARISON_MD,
            duration_minutes=18,
            order_index=1)

    _lesson(db, mod, "linear-time-sorting",
            title="Linear-Time Sorting",
            lesson_type=LessonType.reading,
            content_md=M3_LINEAR_MD,
            duration_minutes=12,
            order_index=2)

    ex_lesson = _lesson(db, mod, "sorting-exercises",
                        title="Sorting — Exercises",
                        lesson_type=LessonType.exercise,
                        content_md=M3_EXERCISE_MD,
                        duration_minutes=35,
                        order_index=3)

    # ── Exercise 3.1: Insertion Sort ─────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "insertion-sort",
        title="Insertion Sort",
        prompt_md=(
            "# Insertion Sort\n\n"
            "Sort **n** integers in ascending order using **Insertion Sort**.\n\n"
            "**Input:**\n```\nn\na₁ a₂ … aₙ\n```\n\n"
            "**Output:** sorted integers separated by spaces\n\n"
            "**Example**\n```\nInput:\n5\n5 3 1 4 2\n\nOutput:\n1 2 3 4 5\n```"
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def insertion_sort(a):\n"
                "    for i in range(1, len(a)):\n"
                "        key = a[i]\n"
                "        j = i - 1\n"
                "        # TODO: shift elements greater than key to the right\n"
                "    return a\n\n"
                "data = sys.stdin.read().split()\n"
                "n = int(data[0])\n"
                "a = list(map(int, data[1:n+1]))\n"
                "print(*insertion_sort(a))\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0], a=d.slice(1,n+1);\n\n"
                "function insertionSort(a) {\n"
                "    for (let i=1;i<a.length;i++) {\n"
                "        let key=a[i], j=i-1;\n"
                "        // TODO\n"
                "        a[j+1]=key;\n"
                "    }\n"
                "    return a;\n"
                "}\n\n"
                "console.log(insertionSort(a).join(' '));\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0], a=d.slice(1,n+1);\n\n"
                "function insertionSort(a: number[]): number[] {\n"
                "    for (let i=1;i<a.length;i++) {\n"
                "        let key=a[i], j=i-1;\n"
                "        while (j>=0 && a[j]>key) { a[j+1]=a[j]; j--; }\n"
                "        a[j+1]=key;\n"
                "    }\n"
                "    return a;\n"
                "}\n\n"
                "console.log(insertionSort(a).join(' '));\n"
            ),
            "java": (
                "import java.util.Scanner;\n"
                "public class Main {\n"
                "    public static void main(String[] args) {\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt();\n"
                "        int[] a=new int[n];\n"
                "        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n"
                "        for(int i=1;i<n;i++) {\n"
                "            int key=a[i],j=i-1;\n"
                "            while(j>=0&&a[j]>key){a[j+1]=a[j];j--;}\n"
                "            a[j+1]=key;\n"
                "        }\n"
                "        StringBuilder sb=new StringBuilder();\n"
                "        for(int i=0;i<n;i++){if(i>0)sb.append(' ');sb.append(a[i]);}\n"
                "        System.out.println(sb);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\n"
                "class Solution {\n"
                "    static void Main() {\n"
                "        int n=int.Parse(Console.ReadLine().Trim());\n"
                "        var a=Array.ConvertAll(Console.ReadLine().Trim().Split(),int.Parse);\n"
                "        for(int i=1;i<n;i++){\n"
                "            int key=a[i],j=i-1;\n"
                "            while(j>=0&&a[j]>key){a[j+1]=a[j];j--;}\n"
                "            a[j+1]=key;\n"
                "        }\n"
                "        Console.WriteLine(string.Join(' ',a));\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "d=sys.stdin.read().split();n=int(d[0]);a=list(map(int,d[1:n+1]))\n"
                "for i in range(1,n):\n"
                "    k=a[i];j=i-1\n"
                "    while j>=0 and a[j]>k: a[j+1]=a[j];j-=1\n"
                "    a[j+1]=k\n"
                "print(*a)\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=128,
        points=15,
    )
    _cases(db, ex, [
        ("basic",    "5\n5 3 1 4 2\n",        "1 2 3 4 5",          False, 1),
        ("sorted",   "5\n1 2 3 4 5\n",        "1 2 3 4 5",          False, 1),
        ("reverse",  "5\n5 4 3 2 1\n",        "1 2 3 4 5",          False, 1),
        ("single",   "1\n42\n",               "42",                  False, 1),
        ("classic",  "6\n64 25 12 22 11 90\n","11 12 22 25 64 90",  True,  2),
        ("dups",     "5\n3 1 4 1 5\n",        "1 1 3 4 5",          True,  2),
    ])

    # ── Exercise 3.2: Merge Sort ──────────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "merge-sort",
        title="Merge Sort",
        prompt_md=(
            "# Merge Sort\n\n"
            "Sort **n** integers in ascending order using **Merge Sort** "
            "(divide-and-conquer, O(n log n)).\n\n"
            "**Input:**\n```\nn\na₁ a₂ … aₙ\n```\n\n"
            "**Output:** sorted integers separated by spaces\n\n"
            "**Example**\n```\nInput:\n6\n5 2 4 6 1 3\n\nOutput:\n1 2 3 4 5 6\n```"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def merge_sort(a):\n"
                "    if len(a) <= 1:\n"
                "        return a\n"
                "    mid = len(a) // 2\n"
                "    left = merge_sort(a[:mid])\n"
                "    right = merge_sort(a[mid:])\n"
                "    return merge(left, right)\n\n"
                "def merge(left, right):\n"
                "    result = []\n"
                "    i = j = 0\n"
                "    # TODO: merge two sorted lists\n"
                "    result.extend(left[i:])\n"
                "    result.extend(right[j:])\n"
                "    return result\n\n"
                "data = sys.stdin.read().split()\n"
                "n = int(data[0])\n"
                "a = list(map(int, data[1:n+1]))\n"
                "print(*merge_sort(a))\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],a=d.slice(1,n+1);\n\n"
                "function mergeSort(a){\n"
                "    if(a.length<=1) return a;\n"
                "    const mid=a.length>>1;\n"
                "    return merge(mergeSort(a.slice(0,mid)),mergeSort(a.slice(mid)));\n"
                "}\n"
                "function merge(l,r){\n"
                "    const res=[];let i=0,j=0;\n"
                "    while(i<l.length&&j<r.length)\n"
                "        res.push(l[i]<=r[j]?l[i++]:r[j++]);\n"
                "    return res.concat(l.slice(i),r.slice(j));\n"
                "}\n\n"
                "console.log(mergeSort(a).join(' '));\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],a=d.slice(1,n+1);\n\n"
                "function mergeSort(a:number[]):number[]{\n"
                "    if(a.length<=1) return a;\n"
                "    const mid=a.length>>1;\n"
                "    return merge(mergeSort(a.slice(0,mid)),mergeSort(a.slice(mid)));\n"
                "}\n"
                "function merge(l:number[],r:number[]):number[]{\n"
                "    const res:number[]=[];let i=0,j=0;\n"
                "    while(i<l.length&&j<r.length) res.push(l[i]<=r[j]?l[i++]:r[j++]);\n"
                "    return res.concat(l.slice(i),r.slice(j));\n"
                "}\n\n"
                "console.log(mergeSort(a).join(' '));\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    static int[] mergeSort(int[] a) {\n"
                "        if (a.length<=1) return a;\n"
                "        int mid=a.length/2;\n"
                "        int[] l=mergeSort(Arrays.copyOfRange(a,0,mid));\n"
                "        int[] r=mergeSort(Arrays.copyOfRange(a,mid,a.length));\n"
                "        return merge(l,r);\n"
                "    }\n"
                "    static int[] merge(int[] l,int[] r){\n"
                "        int[] res=new int[l.length+r.length];\n"
                "        int i=0,j=0,k=0;\n"
                "        while(i<l.length&&j<r.length) res[k++]=(l[i]<=r[j])?l[i++]:r[j++];\n"
                "        while(i<l.length) res[k++]=l[i++];\n"
                "        while(j<r.length) res[k++]=r[j++];\n"
                "        return res;\n"
                "    }\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt();int[] a=new int[n];\n"
                "        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n"
                "        int[] s=mergeSort(a);\n"
                "        StringBuilder sb=new StringBuilder();\n"
                "        for(int i=0;i<s.length;i++){if(i>0)sb.append(' ');sb.append(s[i]);}\n"
                "        System.out.println(sb);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Collections.Generic;\n"
                "class Solution {\n"
                "    static int[] MergeSort(int[] a){\n"
                "        if(a.Length<=1) return a;\n"
                "        int mid=a.Length/2;\n"
                "        var l=MergeSort(a[..mid]);\n"
                "        var r=MergeSort(a[mid..]);\n"
                "        return Merge(l,r);\n"
                "    }\n"
                "    static int[] Merge(int[] l,int[] r){\n"
                "        var res=new List<int>();int i=0,j=0;\n"
                "        while(i<l.Length&&j<r.Length) res.Add(l[i]<=r[j]?l[i++]:r[j++]);\n"
                "        while(i<l.Length) res.Add(l[i++]);\n"
                "        while(j<r.Length) res.Add(r[j++]);\n"
                "        return res.ToArray();\n"
                "    }\n"
                "    static void Main(){\n"
                "        int n=int.Parse(Console.ReadLine().Trim());\n"
                "        var a=Array.ConvertAll(Console.ReadLine().Trim().Split(),int.Parse);\n"
                "        Console.WriteLine(string.Join(' ',MergeSort(a)));\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "def ms(a):\n"
                "    if len(a)<=1: return a\n"
                "    m=len(a)//2; l=ms(a[:m]); r=ms(a[m:])\n"
                "    res=[];i=j=0\n"
                "    while i<len(l) and j<len(r):\n"
                "        if l[i]<=r[j]: res.append(l[i]);i+=1\n"
                "        else: res.append(r[j]);j+=1\n"
                "    return res+l[i:]+r[j:]\n"
                "d=sys.stdin.read().split();n=int(d[0]);a=list(map(int,d[1:n+1]))\n"
                "print(*ms(a))\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=256,
        points=20,
    )
    _cases(db, ex, [
        ("basic",   "6\n5 2 4 6 1 3\n",       "1 2 3 4 5 6",       False, 1),
        ("reverse", "5\n5 4 3 2 1\n",          "1 2 3 4 5",         False, 1),
        ("single",  "1\n99\n",                 "99",                 False, 1),
        ("dups",    "5\n3 1 4 1 5\n",          "1 1 3 4 5",         False, 1),
        ("negs",    "4\n-3 0 -1 2\n",          "-3 -1 0 2",         True,  2),
        ("large",   "8\n8 7 6 5 4 3 2 1\n",    "1 2 3 4 5 6 7 8",   True,  2),
    ])

    # ── Exercise 3.3: Count Inversions ────────────────────────────
    ex, _ = _exercise(db, ex_lesson, "count-inversions",
        title="Count Inversions",
        prompt_md=(
            "# Count Inversions\n\n"
            "An **inversion** in array a[] is a pair (i, j) where i < j but a[i] > a[j].\n\n"
            "Count the total number of inversions.  A sorted array has 0 inversions;\n"
            "a reverse-sorted array of n elements has n(n−1)/2.\n\n"
            "**Input:**\n```\nn\na₁ a₂ … aₙ\n```\n\n"
            "**Output:** number of inversions\n\n"
            "**Example**\n```\nInput:\n5\n2 4 1 3 5\n\nOutput:\n3\n```\n\n"
            "*Hint: Modify Merge Sort — count cross-inversions during the merge step in O(n log n).*"
        ),
        difficulty=Difficulty.hard,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def count_inversions(a):\n"
                "    if len(a) <= 1:\n"
                "        return a, 0\n"
                "    mid = len(a) // 2\n"
                "    left, lc = count_inversions(a[:mid])\n"
                "    right, rc = count_inversions(a[mid:])\n"
                "    merged, mc = merge_count(left, right)\n"
                "    return merged, lc + rc + mc\n\n"
                "def merge_count(left, right):\n"
                "    result = []\n"
                "    count = 0\n"
                "    i = j = 0\n"
                "    while i < len(left) and j < len(right):\n"
                "        if left[i] <= right[j]:\n"
                "            result.append(left[i]); i += 1\n"
                "        else:\n"
                "            # TODO: all remaining left elements form inversions with right[j]\n"
                "            result.append(right[j]); j += 1\n"
                "    result.extend(left[i:])\n"
                "    result.extend(right[j:])\n"
                "    return result, count\n\n"
                "data = sys.stdin.read().split()\n"
                "n = int(data[0])\n"
                "a = list(map(int, data[1:n+1]))\n"
                "_, ans = count_inversions(a)\n"
                "print(ans)\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],a=d.slice(1,n+1);\n\n"
                "function countInv(a){\n"
                "    if(a.length<=1) return [a,0];\n"
                "    const m=a.length>>1;\n"
                "    const [l,lc]=countInv(a.slice(0,m));\n"
                "    const [r,rc]=countInv(a.slice(m));\n"
                "    const [merged,mc]=mergeCount(l,r);\n"
                "    return [merged,lc+rc+mc];\n"
                "}\n"
                "function mergeCount(l,r){\n"
                "    const res=[];let i=0,j=0,cnt=0;\n"
                "    while(i<l.length&&j<r.length){\n"
                "        if(l[i]<=r[j]) res.push(l[i++]);\n"
                "        else{cnt+=l.length-i;res.push(r[j++]);}\n"
                "    }\n"
                "    return[res.concat(l.slice(i),r.slice(j)),cnt];\n"
                "}\n\n"
                "console.log(countInv(a)[1]);\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],a=d.slice(1,n+1);\n\n"
                "function countInv(a:number[]):[number[],number]{\n"
                "    if(a.length<=1) return [a,0];\n"
                "    const m=a.length>>1;\n"
                "    const [l,lc]=countInv(a.slice(0,m));\n"
                "    const [r,rc]=countInv(a.slice(m));\n"
                "    const [merged,mc]=mergeCount(l,r);\n"
                "    return [merged,lc+rc+mc];\n"
                "}\n"
                "function mergeCount(l:number[],r:number[]):[number[],number]{\n"
                "    const res:number[]=[];let i=0,j=0,cnt=0;\n"
                "    while(i<l.length&&j<r.length){\n"
                "        if(l[i]<=r[j]) res.push(l[i++]);\n"
                "        else{cnt+=l.length-i;res.push(r[j++]);}\n"
                "    }\n"
                "    return[res.concat(l.slice(i),r.slice(j)),cnt];\n"
                "}\n\n"
                "console.log(countInv(a)[1]);\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    static long invCount=0;\n"
                "    static int[] mergeSort(int[] a){\n"
                "        if(a.length<=1) return a;\n"
                "        int m=a.length/2;\n"
                "        int[] l=mergeSort(Arrays.copyOfRange(a,0,m));\n"
                "        int[] r=mergeSort(Arrays.copyOfRange(a,m,a.length));\n"
                "        return merge(l,r);\n"
                "    }\n"
                "    static int[] merge(int[] l,int[] r){\n"
                "        int[] res=new int[l.length+r.length];\n"
                "        int i=0,j=0,k=0;\n"
                "        while(i<l.length&&j<r.length){\n"
                "            if(l[i]<=r[j]) res[k++]=l[i++];\n"
                "            else{invCount+=l.length-i;res[k++]=r[j++];}\n"
                "        }\n"
                "        while(i<l.length)res[k++]=l[i++];\n"
                "        while(j<r.length)res[k++]=r[j++];\n"
                "        return res;\n"
                "    }\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt();int[] a=new int[n];\n"
                "        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n"
                "        mergeSort(a);\n"
                "        System.out.println(invCount);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Collections.Generic;\n"
                "class Solution {\n"
                "    static long inv=0;\n"
                "    static int[] MergeSort(int[] a){\n"
                "        if(a.Length<=1) return a;\n"
                "        int m=a.Length/2;\n"
                "        var l=MergeSort(a[..m]);var r=MergeSort(a[m..]);\n"
                "        return Merge(l,r);\n"
                "    }\n"
                "    static int[] Merge(int[] l,int[] r){\n"
                "        var res=new List<int>();int i=0,j=0;\n"
                "        while(i<l.Length&&j<r.Length){\n"
                "            if(l[i]<=r[j])res.Add(l[i++]);\n"
                "            else{inv+=l.Length-i;res.Add(r[j++]);}\n"
                "        }\n"
                "        while(i<l.Length)res.Add(l[i++]);\n"
                "        while(j<r.Length)res.Add(r[j++]);\n"
                "        return res.ToArray();\n"
                "    }\n"
                "    static void Main(){\n"
                "        int n=int.Parse(Console.ReadLine().Trim());\n"
                "        var a=Array.ConvertAll(Console.ReadLine().Trim().Split(),int.Parse);\n"
                "        MergeSort(a);\n"
                "        Console.WriteLine(inv);\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "def ci(a):\n"
                "    if len(a)<=1: return a,0\n"
                "    m=len(a)//2;l,lc=ci(a[:m]);r,rc=ci(a[m:])\n"
                "    res=[];i=j=cnt=0\n"
                "    while i<len(l) and j<len(r):\n"
                "        if l[i]<=r[j]: res.append(l[i]);i+=1\n"
                "        else: cnt+=len(l)-i;res.append(r[j]);j+=1\n"
                "    return res+l[i:]+r[j:],lc+rc+cnt\n"
                "d=sys.stdin.read().split();n=int(d[0]);a=list(map(int,d[1:n+1]))\n"
                "print(ci(a)[1])\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=5000,
        memory_limit_mb=256,
        points=30,
    )
    _cases(db, ex, [
        ("sample",   "5\n2 4 1 3 5\n",    "3",  False, 1),
        ("sorted",   "3\n1 2 3\n",         "0",  False, 1),
        ("reversed", "4\n4 3 2 1\n",       "6",  False, 1),
        ("hidden-1", "6\n5 3 2 4 1 6\n",   "7",  True,  2),
        ("hidden-2", "5\n1 5 2 4 3\n",     "4",  True,  2),
    ])


# ════════════════════════════════════════════════════════════════
#  MODULE 4 — Elementary Data Structures
# ════════════════════════════════════════════════════════════════

M4_ARRAYS_MD = """\
# Arrays and Linked Lists

## Arrays
A contiguous block of memory.  Access any element in **O(1)** by index.

| Operation | Static Array | Dynamic Array |
|-----------|-------------|---------------|
| Access a[i] | O(1) | O(1) |
| Search | O(n) | O(n) |
| Insert/delete at front | O(n) | O(n) |
| Append (back) | O(1) | Amortised O(1) |

**Dynamic arrays** (Python list, Java ArrayList, C++ vector) double capacity
when full: amortised O(1) append via the *accounting / potential* argument.

## Linked Lists
Nodes connected by pointers.  No random access; pointer overhead per node.

| Operation | Singly LL | Doubly LL |
|-----------|-----------|-----------|
| Access by index | O(n) | O(n) |
| Insert at front | O(1) | O(1) |
| Insert at back | O(n) / O(1)* | O(1)* |
| Delete given pointer | O(n)† | O(1) |

*With a tail pointer. †Need to find predecessor.

**Use linked lists when** you need O(1) insertions/deletions at arbitrary
positions and never need random access.
"""

M4_STACKS_MD = """\
# Stacks and Queues

## Stack — Last In, First Out (LIFO)
Operations: **push**, **pop**, **peek/top** — all O(1).

Applications: function call stack, expression evaluation, undo/redo,
DFS (depth-first search), balanced-parenthesis checking.

```
push(x)  → add x to top
pop()    → remove and return top
peek()   → return top without removing
```

## Queue — First In, First Out (FIFO)
Operations: **enqueue**, **dequeue**, **front** — all O(1) (with deque or circular buffer).

Applications: BFS (breadth-first search), task scheduling, print queues.

## Deque (Double-Ended Queue)
Supports O(1) insert/delete at **both** ends.
Python `collections.deque`, Java `ArrayDeque`.

## Classic trick: Queue from two stacks
Inbox stack S1, outbox stack S2.
- Enqueue: push to S1.
- Dequeue: if S2 empty, pop all S1 → push to S2; pop from S2.
Each element moved at most twice → **amortised O(1)** dequeue.

## Monotonic Stack
Maintains elements in monotone order.  Used to solve "next greater element"
in O(n).
"""

M4_EXERCISE_MD = "Practice with stacks, queues, and monotonic stack patterns."


def seed_module4(db: Session, course: Course) -> None:
    mod = _module(db, course, "Elementary Data Structures", 4,
                  "Arrays, linked lists, stacks, queues, and the monotonic stack trick.")

    _lesson(db, mod, "arrays-and-linked-lists",
            title="Arrays and Linked Lists",
            lesson_type=LessonType.reading,
            content_md=M4_ARRAYS_MD,
            duration_minutes=15,
            order_index=1)

    _lesson(db, mod, "stacks-and-queues",
            title="Stacks and Queues",
            lesson_type=LessonType.reading,
            content_md=M4_STACKS_MD,
            duration_minutes=12,
            order_index=2)

    ex_lesson = _lesson(db, mod, "data-structures-exercises",
                        title="Elementary Data Structures — Exercises",
                        lesson_type=LessonType.exercise,
                        content_md=M4_EXERCISE_MD,
                        duration_minutes=30,
                        order_index=3)

    # ── Exercise 4.1: Balanced Parentheses ───────────────────────
    ex, _ = _exercise(db, ex_lesson, "balanced-parentheses",
        title="Balanced Parentheses",
        prompt_md=(
            "# Balanced Parentheses\n\n"
            "Given a string containing only `()[]{}`, determine if the brackets "
            "are properly balanced and nested.\n\n"
            "**Input:** one line containing the bracket string (length 0–10 000)\n\n"
            "**Output:** `YES` if balanced, `NO` otherwise\n\n"
            "**Examples**\n```\n()[]{}  → YES\n([)]    → NO\n{[]}    → YES\n```\n\n"
            "*Hint: use a stack.*"
        ),
        difficulty=Difficulty.easy,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def is_balanced(s):\n"
                "    stack = []\n"
                "    pairs = {')':'(', ']':'[', '}':'{'}\n"
                "    for ch in s:\n"
                "        if ch in '([{':\n"
                "            stack.append(ch)\n"
                "        elif ch in ')]}':\n"
                "            # TODO: check top of stack\n"
                "            pass\n"
                "    return len(stack) == 0\n\n"
                "s = sys.stdin.read().strip()\n"
                "print('YES' if is_balanced(s) else 'NO')\n"
            ),
            "javascript": (
                "const s=require('fs').readFileSync(0,'utf8').trim();\n"
                "const pairs={')':'(',']':'[','}':'{'};\n"
                "const stack=[];\n"
                "let ok=true;\n"
                "for(const ch of s){\n"
                "    if('([{'.includes(ch)) stack.push(ch);\n"
                "    else if(')]}'.includes(ch)){\n"
                "        if(!stack.length||stack[stack.length-1]!==pairs[ch]){ok=false;break;}\n"
                "        stack.pop();\n"
                "    }\n"
                "}\n"
                "console.log(ok&&!stack.length?'YES':'NO');\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const s=fs.readFileSync(0,'utf8').trim();\n"
                "const pairs:Record<string,string>={')':'(',']':'[','}':'{'};\n"
                "const stack:string[]=[];\n"
                "let ok=true;\n"
                "for(const ch of s){\n"
                "    if('([{'.includes(ch)) stack.push(ch);\n"
                "    else if(')]}'.includes(ch)){\n"
                "        if(!stack.length||stack[stack.length-1]!==pairs[ch]){ok=false;break;}\n"
                "        stack.pop();\n"
                "    }\n"
                "}\n"
                "console.log(ok&&!stack.length?'YES':'NO');\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    public static void main(String[] args) {\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        String s=sc.nextLine().trim();\n"
                "        Deque<Character> st=new ArrayDeque<>();\n"
                "        Map<Character,Character> p=Map.of(')','(', ']','[', '}','{');\n"
                "        boolean ok=true;\n"
                "        for(char c:s.toCharArray()){\n"
                "            if(\"([{\".indexOf(c)>=0) st.push(c);\n"
                "            else if(\")]}\".indexOf(c)>=0){\n"
                "                if(st.isEmpty()||st.peek()!=p.get(c)){ok=false;break;}\n"
                "                st.pop();\n"
                "            }\n"
                "        }\n"
                "        System.out.println(ok&&st.isEmpty()?\"YES\":\"NO\");\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Collections.Generic;\n"
                "class Solution {\n"
                "    static void Main(){\n"
                "        var s=Console.ReadLine()?.Trim()??\"\";\n"
                "        var pairs=new Dictionary<char,char>{{')','('},{']','['},{'}','{'}};\n"
                "        var stack=new Stack<char>();\n"
                "        bool ok=true;\n"
                "        foreach(var c in s){\n"
                "            if(\"([{\".Contains(c)) stack.Push(c);\n"
                "            else if(\")]}\".Contains(c)){\n"
                "                if(stack.Count==0||stack.Peek()!=pairs[c]){ok=false;break;}\n"
                "                stack.Pop();\n"
                "            }\n"
                "        }\n"
                "        Console.WriteLine(ok&&stack.Count==0?\"YES\":\"NO\");\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "s=sys.stdin.read().strip()\n"
                "st=[];p={')':'(',']':'[','}':'{'};ok=True\n"
                "for c in s:\n"
                "    if c in '([{': st.append(c)\n"
                "    elif c in ')]}': \n"
                "        if not st or st[-1]!=p[c]: ok=False; break\n"
                "        st.pop()\n"
                "print('YES' if ok and not st else 'NO')\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=3000,
        memory_limit_mb=128,
        points=15,
    )
    _cases(db, ex, [
        ("all-types",    "()[]{}",   "YES", False, 1),
        ("nested-ok",    "{[()]}",   "YES", False, 1),
        ("mismatch",     "([)]",     "NO",  False, 1),
        ("unclosed",     "(",        "NO",  False, 1),
        ("empty",        "",         "YES", False, 1),
        ("extra-close",  "())",      "NO",  True,  1),
        ("deep-nested",  "{[()]}[]", "YES", True,  2),
    ])

    # ── Exercise 4.2: Next Greater Element ───────────────────────
    ex, _ = _exercise(db, ex_lesson, "next-greater-element",
        title="Next Greater Element",
        prompt_md=(
            "# Next Greater Element\n\n"
            "For each element in the array, find the **first element to its right** "
            "that is strictly greater.  If none exists, output **-1**.\n\n"
            "**Input:**\n```\nn\na₁ a₂ … aₙ\n```\n\n"
            "**Output:** n space-separated values\n\n"
            "**Example**\n```\nInput:\n5\n4 5 2 25 7\n\nOutput:\n5 25 25 -1 -1\n```\n\n"
            "*Hint: process right-to-left using a monotone stack — O(n).*"
        ),
        difficulty=Difficulty.medium,
        is_published=True,
        starter_code={
            "python": (
                "import sys\n\n"
                "def next_greater(a):\n"
                "    n = len(a)\n"
                "    result = [-1] * n\n"
                "    stack = []  # monotone decreasing stack of indices\n"
                "    for i in range(n - 1, -1, -1):\n"
                "        # TODO: pop elements from stack that are <= a[i]\n"
                "        # then result[i] = stack top (if any)\n"
                "        stack.append(a[i])\n"
                "    return result\n\n"
                "data = sys.stdin.read().split()\n"
                "n = int(data[0])\n"
                "a = list(map(int, data[1:n+1]))\n"
                "print(*next_greater(a))\n"
            ),
            "javascript": (
                "const d=require('fs').readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],a=d.slice(1,n+1);\n"
                "const res=new Array(n).fill(-1),st=[];\n"
                "for(let i=n-1;i>=0;i--){\n"
                "    while(st.length&&st[st.length-1]<=a[i]) st.pop();\n"
                "    if(st.length) res[i]=st[st.length-1];\n"
                "    st.push(a[i]);\n"
                "}\n"
                "console.log(res.join(' '));\n"
            ),
            "typescript": (
                "import * as fs from 'fs';\n"
                "const d=fs.readFileSync(0,'utf8').trim().split(/\\s+/).map(Number);\n"
                "const n=d[0],a=d.slice(1,n+1);\n"
                "const res=new Array(n).fill(-1),st:number[]=[];\n"
                "for(let i=n-1;i>=0;i--){\n"
                "    while(st.length&&st[st.length-1]<=a[i]) st.pop();\n"
                "    if(st.length) res[i]=st[st.length-1];\n"
                "    st.push(a[i]);\n"
                "}\n"
                "console.log(res.join(' '));\n"
            ),
            "java": (
                "import java.util.*;\n"
                "public class Main {\n"
                "    public static void main(String[] args){\n"
                "        Scanner sc=new Scanner(System.in);\n"
                "        int n=sc.nextInt();\n"
                "        int[] a=new int[n],res=new int[n];\n"
                "        for(int i=0;i<n;i++) a[i]=sc.nextInt();\n"
                "        Arrays.fill(res,-1);\n"
                "        Deque<Integer> st=new ArrayDeque<>();\n"
                "        for(int i=n-1;i>=0;i--){\n"
                "            while(!st.isEmpty()&&st.peek()<=a[i]) st.pop();\n"
                "            if(!st.isEmpty()) res[i]=st.peek();\n"
                "            st.push(a[i]);\n"
                "        }\n"
                "        StringBuilder sb=new StringBuilder();\n"
                "        for(int i=0;i<n;i++){if(i>0)sb.append(' ');sb.append(res[i]);}\n"
                "        System.out.println(sb);\n"
                "    }\n"
                "}\n"
            ),
            "csharp": (
                "using System;\nusing System.Collections.Generic;\n"
                "class Solution {\n"
                "    static void Main(){\n"
                "        int n=int.Parse(Console.ReadLine().Trim());\n"
                "        var a=Array.ConvertAll(Console.ReadLine().Trim().Split(),int.Parse);\n"
                "        var res=new int[n];Array.Fill(res,-1);\n"
                "        var st=new Stack<int>();\n"
                "        for(int i=n-1;i>=0;i--){\n"
                "            while(st.Count>0&&st.Peek()<=a[i]) st.Pop();\n"
                "            if(st.Count>0) res[i]=st.Peek();\n"
                "            st.Push(a[i]);\n"
                "        }\n"
                "        Console.WriteLine(string.Join(' ',res));\n"
                "    }\n"
                "}\n"
            ),
        },
        solution_code={
            "python": (
                "import sys\n"
                "d=sys.stdin.read().split();n=int(d[0]);a=list(map(int,d[1:n+1]))\n"
                "res=[-1]*n;st=[]\n"
                "for i in range(n-1,-1,-1):\n"
                "    while st and st[-1]<=a[i]: st.pop()\n"
                "    if st: res[i]=st[-1]\n"
                "    st.append(a[i])\n"
                "print(*res)\n"
            ),
        },
        supported_languages=LANGS,
        time_limit_ms=3000,
        memory_limit_mb=128,
        points=20,
    )
    _cases(db, ex, [
        ("sample",   "5\n4 5 2 25 7\n",  "5 25 25 -1 -1", False, 1),
        ("all-desc", "4\n13 7 6 12\n",   "-1 12 12 -1",   False, 1),
        ("asc",      "3\n1 2 3\n",       "2 3 -1",         False, 1),
        ("single",   "1\n5\n",           "-1",             False, 1),
        ("hidden-1", "5\n3 1 4 1 5\n",   "4 4 5 5 -1",     True,  2),
        ("hidden-2", "4\n4 4 4 4\n",     "-1 -1 -1 -1",    True,  2),
    ])


# ════════════════════════════════════════════════════════════════
#  Entry point
# ════════════════════════════════════════════════════════════════

def seed() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        # Ensure Algorithms subject exists
        algos = _subject(db, "algorithms",
                         name="Algorithms",
                         description="Core algorithms and data structures.",
                         icon="cpu",
                         color="#3b82f6",
                         order_index=1)

        course = _course(db, algos, "intro-to-algorithms",
                         title="Introduction to Algorithms",
                         summary="Master algorithms from complexity to graphs — MIT 6.006 / CLRS level.",
                         description=(
                             "A comprehensive tour of algorithms and data structures covering: "
                             "asymptotic analysis, sorting (comparison and linear-time), "
                             "fundamental data structures (arrays, linked lists, stacks, queues, "
                             "hash tables, heaps, BSTs, balanced BSTs), graph algorithms "
                             "(BFS, DFS, shortest paths), dynamic programming, and greedy algorithms. "
                             "Based on MIT 6.006 Introduction to Algorithms and the CLRS textbook."
                         ),
                         difficulty="intermediate",
                         estimated_hours=40,
                         is_published=True,
                         order_index=1)

        seed_module1(db, course)
        seed_module2(db, course)
        seed_module3(db, course)
        seed_module4(db, course)

        db.commit()
        print("✓ Modules 1–4 seeded (Getting Started, Big-O, Sorting, Data Structures)")
        print("  Run seed/intro_algorithms_seed_part2.py for modules 5–8")
        print("  Run seed/intro_algorithms_seed_part3.py for modules 9–12")


if __name__ == "__main__":
    seed()
