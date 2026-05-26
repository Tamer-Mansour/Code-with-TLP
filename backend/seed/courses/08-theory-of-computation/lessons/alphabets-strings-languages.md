# Alphabets, Strings, and Languages

Theory of computation begins with the most basic objects: alphabets, strings, and languages. Getting these definitions right is essential — every theorem in the field is stated in terms of them, and every computation problem is ultimately reduced to a question about strings.

## Alphabets

An **alphabet** is a finite, non-empty set of symbols, conventionally denoted Σ (sigma). The requirement of finiteness is not a technicality — it ensures the description of a machine's behaviour stays finite.

| Alphabet | Symbol set |
|----------|-----------|
| Binary   | Σ = {0, 1} |
| Lowercase ASCII | Σ = {a, b, …, z} |
| DNA bases | Σ = {A, C, G, T} |
| Single-letter | Σ = {a} (unary) |

The choice of alphabet is part of defining a problem. When we say "recognize all strings over {0,1}", we are fixing Σ = {0,1}. A different encoding (e.g., base-10 digits) would require a different alphabet, but typically yields an equivalent problem up to a polynomial transformation in string length.

## Strings

A **string** (or **word**) over Σ is any finite sequence of symbols drawn from Σ. Formally, a string of length n is a function w : {1, …, n} → Σ, but we write its values in order: w = w₁w₂…wₙ. The **length** of string w, written |w|, counts its symbols. The unique string of length 0 is the **empty string**, written ε (epsilon).

### String Operations

- **Concatenation**: if x = ab and y = cd then xy = abcd. Concatenation is associative: (xy)z = x(yz). The empty string is the identity: εw = wε = w.
- **Reverse**: wᴿ reverses the order of symbols. (abcd)ᴿ = dcba. (xy)ᴿ = yᴿxᴿ.
- **Power**: wⁿ = w concatenated with itself n times; w⁰ = ε. Example: (ab)³ = ababab.
- **Prefix / Suffix / Substring**: u is a prefix of w if w = uv for some v; a suffix if w = uv for some u; a substring if w = uvz for some u, z.

The set of **all** strings over Σ, including ε, is written **Σ\***. The set of all non-empty strings is Σ⁺ = Σ\* \ {ε}.

### Counting Strings

For a binary alphabet Σ = {0, 1}, the number of strings of each length is:

| Length | Count | Strings |
|--------|-------|---------|
| 0 | 1 | ε |
| 1 | 2 | 0, 1 |
| 2 | 4 | 00, 01, 10, 11 |
| 3 | 8 | 000, 001, …, 111 |
| n | 2ⁿ | … |

In general, |Σⁿ| = |Σ|ⁿ. **Proof by induction**: Base case n=0: |Σ⁰| = 1 = |Σ|⁰. Inductive step: each string of length n+1 is formed by appending one of |Σ| symbols to a string of length n, so |Σⁿ⁺¹| = |Σ|ⁿ · |Σ| = |Σ|ⁿ⁺¹. ∎

Σ\* is therefore countably infinite: we can enumerate its elements in **shortlex order** (by length, then lexicographically within each length), establishing a bijection with ℕ.

## Languages

A **language** over Σ is any subset L ⊆ Σ\*. Languages may be finite or infinite. There is no structural requirement: a language is just a set of strings.

| Language | Description |
|----------|-------------|
| ∅ | The empty language — no strings at all |
| {ε} | The language containing only the empty string |
| {0ⁿ1ⁿ \| n ≥ 0} | Strings of n zeros followed by n ones: ε, 01, 0011, … |
| {w \| w contains an even number of 1s} | An infinite regular language |
| Σ\* | All strings — the "universal" language |

### Operations on Languages

Given languages A and B over Σ:

- **Union**: A ∪ B = {w \| w ∈ A or w ∈ B}
- **Intersection**: A ∩ B = {w \| w ∈ A and w ∈ B}
- **Complement**: Ā = Σ\* \ A (all strings NOT in A)
- **Concatenation**: A∘B = {xy \| x ∈ A, y ∈ B}
- **Kleene star**: A\* = {x₁x₂…xₖ \| k ≥ 0, each xᵢ ∈ A} — zero or more concatenations from A (includes ε since k=0)
- **Kleene plus**: A⁺ = A·A\* = {x₁x₂…xₖ \| k ≥ 1, each xᵢ ∈ A}
- **Difference**: A \ B = A ∩ B̄ = {w \| w ∈ A and w ∉ B}
- **Reversal**: Aᴿ = {wᴿ \| w ∈ A}

These operations form the algebraic backbone of the subject. Notice that Σ\* = Σ\* and ∅\* = {ε} (zero concatenations of strings from ∅ gives ε).

### Worked Examples on Language Operations

Let A = {ε, 0} and B = {1, 10}:

- A ∪ B = {ε, 0, 1, 10}
- A ∩ B = ∅ (no string appears in both)
- A∘B = {1, 10, 01, 010} (pair each word from A with each word from B)
- A\* = {ε, 0, 00, 000, …} = {0ⁿ \| n ≥ 0}

## Computational Problems as Languages

The theory of computation frames every **decision problem** (a problem with a yes/no answer) as a membership question: does string w belong to language L?

For example, the primality problem becomes: let Σ = {0,1} and encode n in binary. Then

> PRIMES = {w ∈ {0,1}\* \| w encodes a prime number in binary}

Asking "is 13 prime?" is the same as asking "is 1101 ∈ PRIMES?" The problem of sorting a list becomes a language recognition problem by encoding input-output pairs. Graph reachability, SAT, and the halting problem all follow this pattern.

This encoding trick is not just a formality. It lets us:
1. Compare the difficulty of different problems using reductions (if A is as hard as B, map instances of A to instances of B).
2. Count and classify problems by cardinality (how many languages exist vs. how many machines can decide them).
3. State universal theorems ("every undecidable language…") that apply to any problem, not just string problems.

## Sets and Relations

- A **set** is an unordered collection of distinct elements. We write x ∈ S for membership, |S| for cardinality (size), and ℙ(S) = 2^S for the power set (set of all subsets).
- A **tuple** (a₁, a₂, …, aₙ) is an ordered sequence. The **Cartesian product** A × B = {(a, b) \| a ∈ A, b ∈ B}.
- A **relation** R ⊆ A × B is a set of pairs. A **function** f : A → B is a relation where each a ∈ A appears in exactly one pair (a, b).
- **Equivalence relation** on A: reflexive (aRa), symmetric (aRb ⟹ bRa), transitive (aRb ∧ bRc ⟹ aRc). Equivalence relations partition A into **equivalence classes**.

## Cardinality and the Language Counting Argument

Two sets have the same **cardinality** if there is a bijection (one-to-one and onto function) between them.

- The natural numbers ℕ, the integers ℤ, the rationals ℚ, and Σ\* for any finite Σ are all **countably infinite** — they all biject with ℕ.
- The real numbers ℝ, the power set ℙ(ℕ), and the set of all languages over {0,1} are **uncountably infinite** — they do NOT biject with ℕ (Cantor's diagonalization argument).

**Key consequence**: The set of all Turing machines is countable (each TM is a finite string, and strings are countable). The set of all languages over {0,1} is uncountable (it is ℙ(Σ\*)). Therefore, **most languages have no deciding Turing machine**. In fact, the decidable languages are a countably infinite set, surrounded by an uncountably infinite sea of undecidable ones. This is not merely a curiosity — it is the root cause of the halting problem's undecidability.
