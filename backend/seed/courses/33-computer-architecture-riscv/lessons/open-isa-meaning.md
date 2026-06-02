# What "Open ISA" Really Means

The word "open" is used liberally in technology, and it does not always mean the same thing. When RISC-V is called an "open ISA," understanding precisely what that means — and what it does not mean — is essential for evaluating its real-world implications.

## Degrees of "Open"

Not all openness is equal. Consider a spectrum:

| Model | Description | Example |
|---|---|---|
| Proprietary, closed | Specification is secret; only the owner implements it | Intel x86 (historically) |
| Licensed, documented | Spec is available under a paid license | ARM (pre-v9 architecture licenses) |
| Open spec, open source impl. | Spec is free; reference implementations are open source | RISC-V |
| Fully open silicon | Spec + RTL + PDKs are all free | RISC-V + OpenROAD + SkyWater 130nm PDK |

RISC-V sits in the third category. The specification documents are freely downloadable, freely implementable, and royalty-free. The specification itself is not "source code" in the programming sense, but it is published openly and governed by a non-profit.

## What "Royalty-Free" Actually Means

A royalty-free ISA means:

- No per-unit fee when you ship a chip.
- No licensing negotiation with a gatekeeper.
- No usage restrictions based on geography, market segment, or company size.
- No risk of the ISA being withdrawn, modified incompatibly, or locked behind new terms.

This is legally codified through the governance structure of **RISC-V International**, a Swiss non-profit. Members contribute to the specification, but no single member can unilaterally change or restrict it.

> **Interview answer:** "An open ISA means the specification is publicly available and royalty-free to implement. Anyone can build a RISC-V processor without paying fees or signing a license agreement, unlike ARM or MIPS."

## What "Open" Does NOT Mean

A common misconception is that "open ISA" means all RISC-V processors are open source. This is false:

- **SiFive** sells commercial RISC-V IP cores — the RTL is proprietary.
- **Alibaba's XuanTie** cores are RISC-V but not fully open source.
- A company can build a completely proprietary chip that implements the RISC-V ISA, ship it, and owe nothing to anyone — that is the point.

Separately, there are genuinely open-source RISC-V implementations:

```
Rocket Chip    — UC Berkeley, Scala/Chisel, BSD license
CVA6 (Ariane)  — ETH Zurich, SystemVerilog, Apache 2.0
PicoRV32       — Claire Wolf, Verilog, ISC license
VexRiscv       — SpinalHDL, MIT license
OpenTitan      — Google/lowRISC, OpenTitan license
```

These are open-source *implementations* of the open *specification*. The distinction matters.

## The Specification Is Stable

One crucial property of an open ISA is long-term stability. RISC-V International maintains strict backward compatibility:

- Code compiled for RV32I in 2015 must run correctly on a 2025 RV32I processor.
- New features are added through **extensions**, not by modifying the base ISA.
- Ratified extensions are frozen; they do not change after ratification.

This stability is enforced by governance, not by a single company's self-interest. It is arguably more trustworthy than a proprietary vendor's backward-compatibility promise.

## Custom Extensions and "Open"

RISC-V explicitly allows implementors to add custom instructions in reserved encoding space. These custom extensions are not open by default — a company's proprietary AI acceleration instructions are their trade secret. The ISA specification merely carves out space for them without conflicting with the standard.

This is an intentional design choice: openness at the standard layer, freedom at the implementation layer.

## A Worked Example: Comparing Licensing

Suppose a startup wants to build a custom processor:

```
ARM Cortex-M0+ license:
  - Sign NDA with Arm Holdings
  - Pay upfront architecture license fee (six figures)
  - Pay per-unit royalty (typically ~1-2% of chip ASP)
  - Agree to usage restrictions and audit rights

RISC-V (e.g., PicoRV32):
  - Download the spec from riscv.org (free)
  - Clone PicoRV32 from GitHub (ISC license, no royalties)
  - Tape out — owe nothing to anyone
```

The legal and financial difference is substantial, especially at low volumes where upfront fees are prohibitive.

## Common Pitfalls

- **Pitfall:** Treating "open ISA" as synonymous with "open source chip." The ISA is open; the implementation may or may not be.
- **Pitfall:** Assuming openness means lack of quality or stability. The RISC-V spec is rigorously maintained and peer-reviewed by hundreds of experts.
- **Pitfall:** Confusing "royalty-free" with "free as in free beer forever." Membership in RISC-V International costs money; the *specification* is free to implement.

The concept of an open ISA is one of the genuinely novel contributions RISC-V makes to the industry — not just technologically, but institutionally and economically.
