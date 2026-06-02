# Video: Context-Free Grammars, Parse Trees, and Chomsky Normal Form

This video builds the theory of context-free languages from grammar rules up through the important normal form used in the CYK algorithm.

**Key takeaways:**
- CFG formal definition: variables, terminals, production rules, and the start variable; leftmost vs. rightmost derivations and the corresponding parse trees.
- How ambiguity arises in grammars (a string with two distinct parse trees) and why it matters for programming language design and parsing.
- Converting any CFG to Chomsky Normal Form (CNF) — the four-step procedure: eliminate ε-productions, unit rules, useless symbols, and then binarize remaining rules.
- Why CNF is the right input format for the CYK membership algorithm and how the grammar size changes under conversion.

**Approximate timestamps:**
- 0:00 – CFG definition and derivation examples
- 20:00 – Parse trees and ambiguity
- 38:00 – CNF motivation and step-by-step conversion
- 58:00 – CYK algorithm preview
