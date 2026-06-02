# RISC-V History and Governance

Understanding where RISC-V came from and who controls it today helps explain why the project is trustworthy as a long-term platform. Unlike most ISAs, RISC-V has a documented academic origin and a transparent governance structure designed to prevent any single party from capturing it.

## Origins at UC Berkeley

RISC-V was created in 2010 at the **University of California, Berkeley** by a research group led by professors **Krste Asanovic** and **David Patterson** (co-author of the seminal textbook *Computer Organization and Design*), along with graduate students Andrew Waterman and Yunsup Lee.

The name "RISC-V" is not a brand name — it is the fifth major RISC ISA to come out of Berkeley research:

| ISA | Year | Notes |
|---|---|---|
| RISC-I | 1981 | First Berkeley RISC research chip |
| RISC-II | 1983 | Improved pipeline |
| SOAR | 1987 | Smalltalk-optimized |
| SPUR | 1988 | Multi-processor research |
| **RISC-V** | **2010** | Open standard; production-ready |

The team designed RISC-V specifically to avoid the accumulated complexity of earlier ISAs. They studied x86, ARM, SPARC, MIPS, and Alpha, retaining only what was well-justified and discarding the rest.

> **Interview answer:** "RISC-V was created at UC Berkeley in 2010 by Krste Asanovic, David Patterson, and collaborators. It is the fifth Berkeley RISC ISA, designed from scratch as a clean, open, and extensible standard."

## From Academia to Industry

The first public release of the RISC-V specification was in 2011. The project gained momentum rapidly:

- **2011** — First public specification released.
- **2014** — First industrial RISC-V symposium held.
- **2015** — **RISC-V Foundation** incorporated as a US non-profit to govern the ISA.
- **2019** — Foundation moves to Switzerland and reincorporates as **RISC-V International** to reduce geopolitical risk from US export regulations.
- **2021** — Ratification of major extensions including Vector (V) and Hypervisor (H).
- **2024** — Over 10 billion RISC-V cores shipped in silicon worldwide.

The move to Switzerland was deliberate and significant. A Swiss-based non-profit is not subject to US export control regulations in the same way a US entity is, which was important for international members who feared that political decisions could affect their access to the ISA.

## RISC-V International: Governance Structure

RISC-V International governs the specification. Its structure is designed to prevent capture by any single company:

```
RISC-V International
  |
  |-- Board of Directors (elected from membership)
  |
  |-- Technical Steering Committee (TSC)
  |     |-- Horizontal committees (security, software, etc.)
  |     |-- Vertical task groups (extensions, profiles)
  |
  |-- Marketing & Ecosystem committees
```

- **Membership tiers:** Premier, Strategic, Community (free for individuals and universities).
- **Specification changes** require consensus within technical task groups and ratification by the TSC and Board.
- **No single member** can block or accelerate a change unilaterally, even founding members.

## How Extensions Get Ratified

A new RISC-V extension goes through a multi-stage process:

1. **Proposal** — A task group drafts the extension specification.
2. **Development** — Public comment period; multiple interoperable implementations required.
3. **Freeze** — Specification text is frozen for final review.
4. **Ratification** — TSC vote; once ratified, the extension is permanently backward-compatible.

This process is slower than a single company making internal decisions, but it produces more stable and carefully reviewed specifications.

## Key People and Institutions

- **Krste Asanovic** — UC Berkeley professor; Chair of RISC-V International Board.
- **David Patterson** — Co-inventor of RISC; Turing Award winner; RISC-V co-creator.
- **Andrew Waterman** — Primary author of the original specification; co-founder of SiFive.
- **SiFive** — First commercial RISC-V CPU company; founded by the original Berkeley team.
- **lowRISC** — UK non-profit producing open-source RISC-V chips (OpenTitan, Ibex).

## Common Pitfalls

- **Pitfall:** Thinking UC Berkeley still controls RISC-V. Governance transferred to RISC-V International in 2015; the university has no special authority.
- **Pitfall:** Assuming RISC-V is too young to be stable. The base ISA (RV32I, RV64I) has been stable and frozen since the early 2010s.
- **Pitfall:** Confusing RISC-V Foundation (original US entity) with RISC-V International (current Swiss entity). The name changed in 2019.

The history of RISC-V illustrates how a university research project can become a global infrastructure standard through deliberate, open governance — a model that distinguishes it from every previous mainstream ISA.
