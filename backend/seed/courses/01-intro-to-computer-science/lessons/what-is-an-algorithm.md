# What Is an Algorithm?

The word "algorithm" is central to computer science, but the concept is older than computers by centuries. The word itself derives from the name of the 9th-century Persian mathematician Muhammad ibn Musa al-Khwarizmi, whose book on arithmetic introduced systematic methods for calculation. Understanding what makes a good algorithm—and what makes a bad one—is the foundation of problem-solving in computing.

## Definition

An **algorithm** is a finite, ordered sequence of unambiguous steps that solves a problem or accomplishes a task.

Key properties—every one is required:

| Property | Meaning | Violation example |
|----------|---------|------------------|
| **Finite** | It must eventually stop | An infinite loop with no exit condition |
| **Ordered** | Steps are carried out in a specific sequence | "Boil water, then add coffee" ≠ "add coffee, then boil" |
| **Unambiguous** | Each step has exactly one clear interpretation | "Add some flour" — how much? |
| **Input** | Zero or more clearly-defined inputs | — |
| **Output** | One or more results that solve the problem | An algorithm that produces no answer is useless |
| **Correct** | It produces the right answer for all valid inputs | An algorithm that works on 90% of inputs is wrong |
| **Effective** | Each step can be carried out in finite time | "Find the largest prime number" — no finite answer |

## A Non-Computer Example: Making Tea

A recipe for making tea is an algorithm:

1. Fill a kettle with fresh cold water.
2. Boil the water.
3. Place a tea bag in a mug.
4. Pour boiling water into the mug.
5. Wait 3–5 minutes depending on desired strength.
6. Remove the tea bag.
7. Add milk and sugar if desired.
8. Serve.

Each step is specific, ordered, and finite. Notice: "Add milk if desired" is a **conditional** step—algorithms can include branching.

## Pseudocode

**Pseudocode** is an informal, language-agnostic way to write algorithms. It uses English-like statements and common programming constructs without worrying about syntax rules of any particular language.

### Finding the Maximum in a List

```
ALGORITHM FindMax(numbers):
    IF numbers is empty:
        RETURN error "empty list"
    max ← numbers[0]
    FOR each n IN numbers:
        IF n > max:
            max ← n
    RETURN max
```

**Trace through with [3, 7, 2, 9, 5]:**

| Step | n | max | Action |
|------|---|-----|--------|
| Init | — | 3 | max = numbers[0] = 3 |
| i=0  | 3 | 3 | 3 > 3? No |
| i=1  | 7 | 7 | 7 > 3? Yes → max = 7 |
| i=2  | 2 | 7 | 2 > 7? No |
| i=3  | 9 | 9 | 9 > 7? Yes → max = 9 |
| i=4  | 5 | 9 | 5 > 9? No |
| Return | — | 9 | ✓ |

Tracing an algorithm manually on a small example is the most reliable way to verify it is correct before coding it.

### Summing a List

```
ALGORITHM Sum(numbers):
    total ← 0
    FOR each n IN numbers:
        total ← total + n
    RETURN total
```

Pseudocode is useful for planning an algorithm before coding it, and for explaining it to others regardless of their preferred programming language.

## Flowcharts

A **flowchart** visualises an algorithm using standard shapes:

- **Oval** — Start / End
- **Rectangle** — Process (action, calculation, assignment)
- **Diamond** — Decision (yes/no branch)
- **Arrow** — Direction of control flow
- **Parallelogram** — Input / Output (optional, used in some conventions)

**Flowchart for FindMax:**

```
      (Start)
         ↓
   [max ← list[0]]
         ↓
   [i ← 1]
         ↓
   ◇ i < len(list)?
    Yes ↓          No → [Return max] → (End)
   ◇ list[i] > max?
    Yes ↓          No ↓
  [max ← list[i]]   ↓
         ↓          ↓
   [i ← i + 1] ←───┘
         └──────────→ back to length check
```

Flowcharts are especially useful when explaining algorithms to non-programmers or when designing complex control flow with many branches.

## Decomposition

**Decomposition** means breaking a large, complex problem into smaller, more manageable sub-problems. This is the most important strategy for tackling hard problems.

**Example: Build a student grade calculator.**

Without decomposition, "build a grade calculator" is overwhelming. With decomposition:

1. Read student names and scores from input
2. For each student, compute their average score
3. Map the average to a letter grade (A/B/C/D/F)
4. Display a formatted report

Each sub-problem can be solved independently and tested separately. This is also the principle behind **functions** in programming—each function solves one well-defined sub-problem.

**The Rule:** If you cannot explain a function in one sentence, it probably needs to be decomposed further.

## Algorithm Efficiency: Why It Matters

Two algorithms can solve the same problem but take very different amounts of time. This is measured using **Big-O notation**, which describes how the time (or memory) required grows as the input size grows.

### Concrete Comparison

Problem: Is the number 5 present in a list of *n* numbers?

**Linear search** — check each element one by one:
- Best case: target is first → 1 check
- Worst case: target is last or absent → n checks

**Binary search** — only works on a sorted list; repeatedly halve the search space:
- Worst case: log₂(n) checks

| Input size n | Linear search (worst) | Binary search (worst) |
|-------------|----------------------|-----------------------|
| 100 | 100 comparisons | 7 comparisons |
| 1,000 | 1,000 | 10 |
| 1,000,000 | 1,000,000 | 20 |
| 1,000,000,000 | 1,000,000,000 | 30 |

Binary search is 50,000,000× faster for a billion-item list! The right algorithm is orders of magnitude more powerful than faster hardware.

### Informal Big-O Categories

| Notation | Name | Example |
|----------|------|---------|
| O(1) | Constant | Array index lookup |
| O(log n) | Logarithmic | Binary search |
| O(n) | Linear | Linear search |
| O(n log n) | Linearithmic | Merge sort |
| O(n²) | Quadratic | Bubble sort |
| O(2ⁿ) | Exponential | Trying all subsets (brute force) |

## Good Algorithm Design Principles

1. **Correctness first** — an elegant but wrong algorithm is useless. Test every edge case.
2. **Clarity** — write pseudocode before code. Name variables meaningfully.
3. **Decompose** — solve one sub-problem at a time. Write one function per concern.
4. **Trace manually** — walk through your algorithm on 2–3 examples before coding it.
5. **Consider edge cases** — empty input, single element, duplicates, negative numbers, maximum size.
6. **Analyse efficiency** — for small inputs, any algorithm works. For large inputs, O(n²) is unacceptable when O(n log n) exists.

## Worked Design Example: FizzBuzz

**Problem:** Print the numbers 1–100. For multiples of 3, print "Fizz". For multiples of 5, print "Buzz". For multiples of both, print "FizzBuzz".

**Step 1 — Decompose:** For each number from 1 to 100, decide what to print. That's the whole thing.

**Step 2 — Pseudocode:**

```
FOR n FROM 1 TO 100:
    IF n MOD 15 == 0:
        PRINT "FizzBuzz"
    ELSE IF n MOD 3 == 0:
        PRINT "Fizz"
    ELSE IF n MOD 5 == 0:
        PRINT "Buzz"
    ELSE:
        PRINT n
```

**Step 3 — Trace (n=1, 3, 5, 15):**
- n=1: none of 1%15, 1%3, 1%5 == 0 → print 1 ✓
- n=3: 3%3 == 0 → print "Fizz" ✓
- n=5: 5%5 == 0 → print "Buzz" ✓
- n=15: 15%15 == 0 → print "FizzBuzz" ✓

**Note:** The order of the checks matters. If we checked `n % 3 == 0` before `n % 15 == 0`, we would print "Fizz" for 15 instead of "FizzBuzz". This is a classic example of edge-case order mattering.

## Common Misconceptions

**"A program is an algorithm."**
A program is an implementation of one or more algorithms in a specific language. The algorithm is the abstract idea; the program is the concrete realisation. The same algorithm can be implemented in Python, Java, or assembly—it is the same algorithm in all three.

**"The fastest algorithm is always best."**
Not always. A more efficient algorithm may be much harder to understand and maintain. For small inputs, a simple O(n²) sort is fine and easier to debug than a complex O(n log n) sort. Choose efficiency when the input size demands it.

**"Pseudocode has to use specific keywords or formatting."**
Pseudocode has no standard—any clear, unambiguous description of an algorithm's logic is valid pseudocode. Its purpose is communication, not execution.

## Key Takeaways

- An algorithm is a finite, ordered, unambiguous sequence of steps that produces a correct output for any valid input.
- **Pseudocode** expresses an algorithm in plain language; **flowcharts** visualise it—both are for human communication, not execution.
- **Decomposition** breaks hard problems into manageable, independently solvable pieces.
- Algorithm efficiency matters enormously as data grows—binary search (O(log n)) beats linear search (O(n)) by millions of times for large data.
- Always trace your algorithm manually on examples and edge cases before coding it.
