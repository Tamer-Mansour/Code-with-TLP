# Encoding and Cardinality

Before any machine can process a mathematical object (graph, number, automaton), that object must be encoded as a string. This lesson makes encoding precise, explains the shortlex enumeration of Σ*, and establishes the cardinality gap between programs and languages — the root cause of undecidability.

## Encoding Objects as Strings

We write ⟨O⟩ or ⟨O₁, O₂⟩ for the **encoding** of object(s) as a string over some fixed alphabet. The exact encoding rarely matters — what matters is that it satisfies three properties:

1. **Computably producible**: a Turing machine can generate ⟨O⟩ from O.
2. **Computably parseable**: a Turing machine can recover O from ⟨O⟩ (the encoding is injective).
3. **Polynomially reasonable**: |⟨O⟩| is polynomial in the natural size of O. (A unary encoding of n would have length n, which is exponentially larger than binary — this makes polynomial-time algorithms appear exponential.)

### Standard Encodings

| Object | Natural size | Encoding |
|--------|-------------|----------|
| Integer n | ⌊log₂ n⌋ + 1 bits | Binary representation. ⟨13⟩ = 1101. |
| Pair (a, b) over Σ | \|a\| + \|b\| | Use a separator symbol not in Σ, or a length-prefixed scheme. |
| Tuple (a₁, …, aₖ) | Σ\|aᵢ\| | k-1 separators, or self-delimiting. |
| Graph G = (V, E) | O(V + E) | Adjacency list: "n;m;u₁v₁;u₂v₂;…" where n=\|V\|, m=\|E\|. |
| DFA M = (Q, Σ, δ, q₀, F) | O(\|Q\|²·\|Σ\|) | Encode \|Q\|, \|Σ\|, then the transition table row by row. |
| CFG G = (V, Σ, R, S) | O(sum of rule lengths) | Encode number of variables, rules, then each rule. |

When we write

> A_DFA = {⟨M, w⟩ \| M is a DFA and M accepts w}

we mean the set of all strings that, when parsed as an encoding of a DFA M and a string w, satisfy the condition M accepts w. The encoding convention is part of the language definition, but any reasonable encoding gives the same decidability results.

### Why Encoding Details Do Not Matter for Decidability

**Theorem.** If A is decidable (resp. Turing-recognizable) under encoding scheme E₁, it is also decidable (resp. Turing-recognizable) under any other polynomially-equivalent encoding scheme E₂.

*Proof sketch.* Given a decider D for E₁-encodings, construct a decider D' for E₂-encodings: D' first converts the E₂-encoding to E₁-encoding (computable in poly time), then runs D. Since both conversions are computable, D' is a valid TM. ∎

This justifies the informal notation we use throughout the course.

## Countable vs. Uncountable Sets

**Definition.** A set S is **countably infinite** if there exists a bijection f : ℕ → S. Equivalently, S's elements can be listed without repetition in a (possibly infinite) sequence s₀, s₁, s₂, …

A set is **countable** if it is finite or countably infinite.

### Examples of Countable Sets

- **ℕ = {0, 1, 2, …}**: trivially listed in order.
- **ℤ = {…, -2, -1, 0, 1, 2, …}**: list as 0, 1, -1, 2, -2, 3, -3, …
- **ℚ**: list all fractions p/q with p ∈ ℤ, q ∈ ℕ⁺, gcd(|p|, q)=1 by the Cantor dovetailing argument (diagonalize the grid of pairs).
- **Σ\* for any finite Σ**: enumerate in shortlex order (see below).
- **The set of all finite subsets of ℕ**: each is a finite set of naturals, encodeable as a sorted list.

### Shortlex Enumeration of Σ*

For Σ = {0, 1}, enumerate Σ\* first by length, then lexicographically within each length:

| Index | String |
|-------|--------|
| 0 | ε |
| 1 | 0 |
| 2 | 1 |
| 3 | 00 |
| 4 | 01 |
| 5 | 10 |
| 6 | 11 |
| 7 | 000 |
| 8 | 001 |
| … | … |

The formula: string at index i corresponds to the binary representation of (i+1) with the leading 1 stripped. For example, index 5 → 6 in binary → 110 → strip leading 1 → "10". This gives an explicit computable bijection ℕ → Σ\*, confirming Σ\* is countably infinite.

## Cantor's Theorem: ℙ(ℕ) is Uncountable

**Theorem (Cantor, 1891).** The power set ℙ(ℕ) — equivalently, the set of all infinite binary sequences — is uncountably infinite.

**Proof (diagonalization).** Suppose for contradiction that ℙ(ℕ) is countable with enumeration S₀, S₁, S₂, … Define a new subset D ⊆ ℕ by: n ∈ D ⟺ n ∉ Sₙ. Then D differs from every Sₙ: D differs from Sₙ at position n (n ∈ D iff n ∉ Sₙ). So D is not in the enumeration, contradicting the assumption that the enumeration listed all subsets. ∎

Since each subset S ⊆ ℕ corresponds to its characteristic function (the infinite binary sequence where the i-th bit is 1 iff i ∈ S), this proves the set of infinite binary sequences is uncountable. The real numbers in [0,1] in binary form such sequences, confirming |ℝ| > |ℕ|.

## The Fundamental Cardinality Gap

Two crucial observations:

1. **The set of all Turing machines is countably infinite.** Each TM is a finite string over some alphabet, and Σ\* is countable. So we can list all TMs: M₀, M₁, M₂, …

2. **The set of all languages over {0,1} is uncountably infinite.** A language is a subset of {0,1}\*. Since {0,1}\* ≅ ℕ (both countably infinite), the set of all languages is ℙ({0,1}\*) ≅ ℙ(ℕ), which is uncountable by Cantor's theorem.

**Conclusion.** |{TMs}| = ℵ₀ (countably infinite) < |{languages}| = 2^{ℵ₀} (uncountably infinite). Therefore most languages cannot be recognized by any Turing machine. In fact, the Turing-recognizable (recursively enumerable) languages are a **countable** set — a set of measure zero among all languages.

## The Diagonal Language

The diagonalization argument gives a concrete example of a non-Turing-recognizable language:

> D = {⟨M⟩ \| M is a TM that does not accept ⟨M⟩}

**Theorem.** D is not Turing-recognizable.

**Proof.** Suppose TM R recognizes D. Consider running R on input ⟨R⟩:
- If R accepts ⟨R⟩: then ⟨R⟩ ∈ D by the definition of L(R). But ⟨R⟩ ∈ D means R does not accept ⟨R⟩ — contradiction.
- If R does not accept ⟨R⟩: then ⟨R⟩ ∉ L(R), meaning ⟨R⟩ ∈ D (R doesn't accept its own encoding). Since R recognizes D, R should accept ⟨R⟩ — contradiction.

Both cases are impossible, so R cannot exist. ∎

This is the direct automata-theoretic counterpart of Cantor's diagonalization. The encoding ⟨M⟩ plays the role of the index i in Cantor's proof; "M does not accept ⟨M⟩" plays the role of "i ∉ Sᵢ".

## Practical Upshot

The encoding apparatus might seem purely theoretical, but it has practical consequences:
- Debuggers, interpreters, and compilers all take program descriptions as input. The fact that programs are strings is not just notation — it enables programs to *reason about programs*.
- The A_TM language (does TM M accept w?) is the archetype of all undecidable properties. Every time you write a static analysis tool or a type checker that asks "can this program ever reach state X?", you are approximating an undecidable problem, and the tool must necessarily be incomplete or unsound.
- The gap between countable programs and uncountable languages means no matter how many programs humanity writes, there will always be infinitely many more problems that no program can solve.
