# Decidability and the Halting Problem

The most famous result in computability theory is that the **halting problem** — deciding whether a given program halts on a given input — is **undecidable**: no algorithm can solve it in general. This lesson proves this rigorously and develops the reduction technique for propagating undecidability.

## Key Definitions

A language L is:
- **Decidable** (recursive): there is a TM that always halts and accepts exactly the strings in L.
- **Turing-recognizable** (recursively enumerable, r.e.): there is a TM that accepts exactly the strings in L (may loop on strings not in L).
- **Co-Turing-recognizable** (co-r.e.): the complement L̄ is Turing-recognizable.

**Theorem.** L is decidable if and only if L is both Turing-recognizable and co-Turing-recognizable.

*Proof (⟹):* A decider for L is also a recognizer for L and for L̄.

*Proof (⟸):* Let M₁ recognize L and M₂ recognize L̄. Build decider D: run M₁ and M₂ simultaneously (on alternating steps). Every input w is either in L (M₁ accepts eventually) or in L̄ (M₂ accepts eventually). So D always halts. ∎

## The Acceptance Problem A_TM

Define:
> **A_TM** = {⟨M, w⟩ \| M is a TM and M accepts w}

**Theorem (Turing, 1936).** A_TM is undecidable.

### Proof by Diagonalization

**A_TM is Turing-recognizable.** The universal TM U takes input ⟨M, w⟩, simulates M on w step by step, and accepts if M accepts. If M loops, U loops. So U recognizes A_TM.

**A_TM is not decidable.** Suppose for contradiction that H is a TM that **decides** A_TM. Construct a new TM D:

```
D(⟨M⟩):
    Run H on input ⟨M, ⟨M⟩⟩.
    If H accepts: D REJECTS.
    If H rejects: D ACCEPTS.
```

Now consider D on input ⟨D⟩:

- **Case 1:** D accepts ⟨D⟩. Then H accepted ⟨D, ⟨D⟩⟩, meaning "D accepts ⟨D⟩" is true. But D was built to *reject* when H accepts. Contradiction.
- **Case 2:** D rejects ⟨D⟩. Then H rejected ⟨D, ⟨D⟩⟩, meaning "D accepts ⟨D⟩" is false, i.e., D does not accept ⟨D⟩. But D was built to *accept* when H rejects. Contradiction.

Both cases are impossible, so H cannot exist. A_TM is undecidable. ∎

**Corollary.** A_TM is not co-Turing-recognizable (since it is Turing-recognizable but not decidable, its complement cannot also be Turing-recognizable, or we'd have a decider).

## The Halting Problem HALT_TM

Define:
> **HALT_TM** = {⟨M, w⟩ \| M is a TM and M halts on input w}

**Theorem.** HALT_TM is undecidable.

**Proof by reduction from A_TM.** We show A_TM ≤_m HALT_TM: if HALT_TM were decidable, so would A_TM be.

Given ⟨M, w⟩, construct ⟨M', w⟩ where M' simulates M on w, but M' **loops** (rather than halts and rejects) whenever M would reject. Specifically:

```
M'(w):
    Simulate M on w.
    If M accepts: ACCEPT.
    If M rejects: run in an infinite loop.
```

Then: M accepts w ⟺ M' accepts w ⟺ M' halts on w (since M' only halts by accepting).

So ⟨M, w⟩ ∈ A_TM ⟺ ⟨M', w⟩ ∈ HALT_TM. The function f(⟨M, w⟩) = ⟨M', w⟩ is computable (we just described it). Thus A_TM ≤_m HALT_TM.

If HALT_TM were decidable by decider D_H, then running D_H on f(⟨M, w⟩) would decide A_TM — but A_TM is undecidable. Contradiction. So HALT_TM is undecidable. ∎

## More Undecidable Languages

| Language | Definition | Proof method |
|----------|-----------|-------------|
| A_TM | Does M accept w? | Diagonalization |
| HALT_TM | Does M halt on w? | Reduction from A_TM |
| E_TM | Is L(M) = ∅? | Reduction from A_TM |
| EQ_TM | Is L(M₁) = L(M₂)? | Reduction from E_TM |
| REGULAR_TM | Is L(M) regular? | Reduction from A_TM (via Rice's theorem) |

### Proving E_TM Undecidable

E_TM = {⟨M⟩ \| L(M) = ∅}.

**Proof.** Reduce A_TM ≤_m E_TM. Given ⟨M, w⟩, construct ⟨M'⟩ where:

```
M'(x):
    Ignore x entirely.
    Simulate M on w.
    If M accepts: ACCEPT.
```

Then L(M') = Σ\* if M accepts w (M' accepts every input), and L(M') = ∅ if M does not accept w.

So ⟨M, w⟩ ∈ A_TM ⟺ L(M') ≠ ∅ ⟺ ⟨M'⟩ ∉ E_TM.

The mapping f(⟨M, w⟩) = ⟨M'⟩ is computable. Therefore A_TM ≤_m Ē_TM (complement of E_TM). Since A_TM is undecidable, Ē_TM is undecidable, and hence E_TM is undecidable. ∎

## Rice's Theorem

**Theorem (Rice, 1953).** Every **non-trivial property** of the language of a Turing machine is undecidable.

**Formal statement:** Let P be a property of Turing-recognizable languages (a set of Turing-recognizable languages). Define:

> L_P = {⟨M⟩ \| L(M) ∈ P}

P is **trivial** if either every Turing-recognizable language has P, or no Turing-recognizable language has P. Otherwise P is non-trivial.

**Theorem.** If P is non-trivial, L_P is undecidable.

**Proof sketch.** Let T_∅ be a TM that always rejects (L(T_∅) = ∅). Since P is non-trivial, there exists a Turing-recognizable language L₀ ∈ P with L₀ ≠ ∅ (or vice versa; assume ∅ ∉ P WLOG). Let M₀ be a TM with L(M₀) = L₀.

Given ⟨M, w⟩, construct M' that on input x: simulates M on w; if M accepts, simulates M₀ on x; accepts if M₀ accepts. So L(M') = L₀ if M accepts w, and L(M') = ∅ if M does not accept w.

Since L₀ ∈ P and ∅ ∉ P: ⟨M, w⟩ ∈ A_TM ⟺ ⟨M'⟩ ∈ L_P. Thus A_TM ≤_m L_P, proving L_P undecidable. ∎

**Consequences.** All of the following are undecidable:
- "L(M) contains at least 2 strings."
- "L(M) = {ε}."
- "L(M) is infinite."
- "L(M) is regular / context-free / decidable."
- "L(M) = Σ\*."

Rice's theorem is a powerful black box: any non-trivial semantic property of a TM's language is undecidable, period. Note it applies to **semantic** properties (about L(M)), not **syntactic** properties (about the description of M). For example, "M has fewer than 100 states" is a syntactic property and is decidable.
