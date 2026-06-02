# Video: Regular Expressions, the Pumping Lemma, and Limits of Regular Languages

This video covers the algebraic side of regular languages — regular expressions and their equivalence to finite automata — then introduces the pumping lemma as a tool to prove a language is *not* regular.

**Key takeaways:**
- Regular expression syntax and semantics: union (|), concatenation, Kleene star (*), and how they map to NFA constructions (Thompson's construction).
- Proving RE ↔ NFA equivalence: every RE has an NFA, every NFA can be converted to a RE (via state elimination / GNFA).
- How to apply the pumping lemma: pick a pumping string, show that every decomposition xyz leads to a contradiction, conclude non-regularity.
- Classic non-regular examples: {0ⁿ1ⁿ}, {ww}, {1^(p) | p is prime}.

**Approximate timestamps:**
- 0:00 – Regular expression definition and examples
- 18:00 – Thompson's NFA construction from a RE
- 35:00 – GNFA and RE from NFA (state elimination)
- 52:00 – Pumping lemma statement and proof sketch
- 1:05:00 – Pumping lemma applications
