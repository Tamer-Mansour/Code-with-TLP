# Regular Expressions

A **regular expression** (regex) is a concise algebraic notation for describing regular languages. The theoretical definition is more restricted than "extended regex" in Perl or Python — no backreferences, no lookaheads — yet it captures exactly the same class as finite automata: the regular languages. This equivalence (Kleene's theorem, 1956) is one of the most beautiful results in the theory.

## Formal Definition

The set of regular expressions over alphabet Σ is defined inductively:

**Base cases** (atomic regexes):
- **∅** is a regex denoting the empty language {}.
- **ε** is a regex denoting {ε} (the language containing only the empty string).
- **a** for any a ∈ Σ is a regex denoting {a}.

**Inductive cases** — if R and S are regexes:
- **(R ∪ S)** — alternation: L(R ∪ S) = L(R) ∪ L(S). Also written R|S.
- **(R ∘ S)** or **(RS)** — concatenation: L(RS) = L(R)·L(S).
- **(R\*)** — Kleene star: L(R\*) = L(R)\*.

Standard precedence (high to low): \* > concatenation > |.

## Examples

| Expression | Language |
|-----------|----------|
| 0\*1 | Strings of zero or more 0s followed by a single 1 |
| (0∪1)\* | All binary strings (Σ\*) |
| (0∪1)\*11(0∪1)\* | Binary strings containing "11" as a substring |
| (0\*10\*1)\*0\* | Binary strings with an even number of 1s |
| (01∪10)\* | Strings of concatenated "01" and "10" pairs |
| ε∪1(0∪1)\* | Binary strings that are ε or start with 1 |
| (a∪b)\*a(a∪b)(a∪b) | Strings over {a,b} where the third-from-last symbol is 'a' |

## Equivalence to Finite Automata (Kleene's Theorem)

**Theorem (Kleene, 1956).** A language L is regular if and only if some regular expression describes L.

The proof goes in two directions.

### Direction 1: Regex → NFA (Thompson's Construction)

Given a regular expression R, build an NFA N with L(N) = L(R) by structural induction on R. Each NFA has exactly one accept state and no transitions out of the accept state.

**Base cases:**

- R = ∅: NFA with start state q₀, accept state q_a, no transitions.
- R = ε: NFA with q₀ →ε q_a.
- R = a: NFA with q₀ →^a q_a.

**Inductive cases** (let N₁ and N₂ be NFAs for R₁ and R₂):

- **R₁ ∪ R₂**: Add new start q₀ with ε-transitions to starts of N₁ and N₂; add new accept q_a with ε-transitions from accepts of N₁ and N₂.
- **R₁R₂**: Connect N₁'s accept to N₂'s start via ε; N₂'s accept is the new accept.
- **R₁\***: Add new start/accept q₀; add ε from q₀ to N₁'s start, ε from N₁'s accept to q₀.

**Size guarantee:** The NFA has at most 2|R| states (where |R| is the number of operators and symbols in R). This construction is called **Thompson's construction** (Ken Thompson, 1968) and is the basis of most regex engines.

### Direction 2: DFA → Regex (GNFA Method)

A **generalized NFA (GNFA)** is an NFA whose transitions are labeled with regular expressions (not just single symbols). The GNFA starts with an arrow from a dedicated start state, and has a single dedicated accept state with arrows arriving from all other states.

**Algorithm (state elimination):**
1. Convert DFA to GNFA by adding a new start with ε to original start, and a new accept with ε-transitions from all original accept states.
2. Repeatedly remove an intermediate state q (not the special start or accept). For every pair (qᵢ, qⱼ) with edges qᵢ → q and q → qⱼ, add a new edge labeled (R₁)(R₂)\*(R₃) where R₁ is the label qᵢ→q, R₂ is the self-loop at q, R₃ is the label q→qⱼ. Union with any existing edge qᵢ→qⱼ.
3. When only start and accept remain, the single edge's label is the desired regex.

## Worked Derivation: Even Number of 1s

Build a regex for L = {w ∈ {0,1}\* \| w contains an even number of 1s}.

**The minimal DFA** has 2 states: q₀ (even count of 1s seen, start+accept) and q₁ (odd count):

| State | 0 | 1 |
|-------|---|---|
| q₀ | q₀ | q₁ |
| q₁ | q₁ | q₀ |

**Apply state elimination** with the GNFA method:

Add start state q_s (ε to q₀) and accept state q_a (ε from q₀). Eliminate q₁:

- q₀ → q₁ (label: 1); q₁ → q₀ (label: 1); self-loop at q₁ (label: 0)
- New edge q₀ → q₀: label = 10\*1 (go to q₁ via 1, loop on 0, come back via 1)
- Existing q₀ → q₀ self-loop: 0

Combined q₀ self-loop: (0 ∪ 10\*1)

Apply Kleene star and prefix with start, suffix with accept:

**Final regex: (0 ∪ 10\*1)\***

Verify: "1100" — match "11" as 10\*1 (with 0\* = ε), then "00" as 0, then 0. Actually in (0 ∪ 10\*1)\*: "1100" = "10\*1" (where middle 0\* = one 0, giving "100"? No. Let's be careful: 10\*1 matches 1·(zero or more 0s)·1, so it matches "11" (0\* = ε) or "101" (0\* = 0) or "1001", etc. The string "1100" = "11"·"00" = (10\*1 with 0\*=ε) · (0·0). So "1100" ∈ (0 ∪ 10\*1)\*. Correct — "1100" has two 1s, which is even. ✓

An alternative equivalent regex derived more directly: **(0\*10\*1)\*0\***.

Verify: "1100": match (0\*10\*1) twice? That needs 4 ones. Instead: match "11" as (0\*=ε, 1, 0\*=ε, 1), then "00" as 0\*. Yes! "(ε·1·ε·1)·00" — one iteration of (0\*10\*1) gives "11", then 0\* gives "00". ✓

## Practical Notes

- Regular expressions in tools like `grep`, Python `re`, or POSIX extend the formal definition with shortcuts: `[abc]` = a∪b∪c, `+` = R·R\*, `?` = ε∪R, `{n,m}` for counted repetitions. These are syntactic sugar over the formal definition and describe the same regular languages.
- **Backreferences** like `\1` (match the same text captured by group 1) go *beyond* the theoretical model and can describe non-regular languages. For example, `(.+)\1` matches "ww" — and {ww \| w ∈ Σ\*} is not regular (proved with the pumping lemma). This is why regex engines with backreferences can be exponentially slow on pathological inputs.
- In practice, Thompson's construction + subset construction gives a DFA-based regex engine with O(n) matching time (after O(|R|·2^|R|) preprocessing). Backtracking NFA engines (like Python `re`) can be O(2^n) in the worst case.
