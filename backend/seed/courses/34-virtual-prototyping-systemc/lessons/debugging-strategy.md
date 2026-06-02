# A Debugging Strategy for Virtual Platforms

Virtual prototypes are powerful precisely because they give you total observability — but that power is wasted without a systematic debugging strategy. A random "let me add a print statement and see" approach rarely works when the bug could be anywhere in the software stack, the instruction-set simulator, a TLM model, or the interconnect timing. This lesson lays out a structured triage process you can follow every time.

## The Layered Mental Model

Before touching a single tool, mentally locate the bug in one of these layers:

| Layer | Examples of failure |
|---|---|
| Software logic | Wrong algorithm, bad pointer arithmetic |
| ABI / calling convention | Corrupt stack, wrong register usage |
| Memory map | Driver writing to wrong address |
| Peripheral model | Register not implemented, wrong interrupt line |
| Bus / TLM model | Transport error, incorrect response status |
| ISS (CPU model) | Wrong instruction decode, flag error |

Work top-down. Software bugs are far more common than model bugs, so rule them out first.

## The Five-Step Strategy

**1. Reproduce the failure deterministically.**
Virtual prototypes are deterministic by construction (no real-time hardware). Record the exact simulation command, seed, and binary. A bug you cannot reliably reproduce cannot be reliably fixed.

**2. Narrow the time window.**
Use the simulator's cycle counter or `sc_time_stamp()`. Add a simple timestamp log:

```cpp
SC_METHOD(monitor);
sensitive << clk.pos();

void monitor() {
    if (stuck_flag)
        SC_REPORT_WARNING("DEBUG", ("Stuck at " + sc_time_stamp().to_string()).c_str());
}
```

Find the first bad event; everything before it is clean.

**3. Isolate the subsystem.**
Replace suspect models with golden stubs. If the real UART model is suspect, swap it for a stub that logs every register access and returns a fixed value. If the bug disappears, the model is guilty.

**4. Confirm with a known-good reference.**
Run the same binary on real hardware, QEMU, or a reference ISS. If behavior differs, the delta is your bug. If behavior is the same, the bug is in the software.

**5. Fix one thing at a time.**
Two concurrent fixes obscure causality. Version-control every change so you can bisect.

## Common Pitfalls

- **Printing too much.** Flooding the terminal with every bus transaction hides the signal in noise. Use conditional logging gated on a verbosity flag.
- **Assuming the ISS is correct.** An ISS can have subtle flag-setting bugs that only manifest for rare instruction combinations. When in doubt, diff against a reference trace.
- **Ignoring simulation warnings.** SystemC `SC_REPORT_WARNING` calls are often dismissed. Treat them as first-class bugs — they usually point directly at unimplemented features or out-of-range accesses.
- **Debugging with release builds.** Always compile both the virtual platform and the guest binary with debug symbols (`-g -O0`) during debugging. Optimized builds inline and reorder code, making correlation between source and trace nearly impossible.

## Quick Checklist

- [ ] Can you reproduce the failure with the same binary every run?
- [ ] Do you know the simulation time at which failure first occurs?
- [ ] Have you ruled out the software layer?
- [ ] Have you ruled out the memory map / linker script?
- [ ] Are all peripherals accessed via their documented register offsets?

> **Interview answer:** "I start by isolating which layer contains the bug — software, memory map, peripheral model, or ISS — using deterministic reproduction and stub replacement, before reaching for gdb or trace tools."
