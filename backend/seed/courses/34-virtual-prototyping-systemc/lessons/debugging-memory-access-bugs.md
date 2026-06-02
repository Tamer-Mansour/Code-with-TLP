# Debugging Memory-Access Bugs

Memory-access bugs — null pointer dereferences, buffer overflows, use-after-free, and wild pointer writes — are responsible for the majority of embedded software crashes. On a virtual prototype, you have tools to catch them at the exact faulting instruction, not just at the symptom.

## Categories of Memory-Access Bugs

| Bug type | Typical symptom | Root cause |
|---|---|---|
| NULL dereference | Data/prefetch abort at addr 0 | Uninitialized pointer |
| Out-of-bounds write | Corruption of adjacent struct fields | Missing bounds check |
| Stack overflow | Abort when sp crosses stack limit | Deep recursion or large locals |
| Use-after-free | Non-deterministic corruption | Freed memory reused |
| Wild pointer | Abort at random MMIO address | Arithmetic error on pointer |
| Unaligned access | Bus error or silent misread | Casting between misaligned types |

## Technique 1: gdb Watchpoints

Set a hardware watchpoint on the address being corrupted. The VP will stop at the exact write instruction:

```
(gdb) watch *((uint32_t *)0x20001048)
Hardware watchpoint 1: *((uint32_t *)0x20001048)
(gdb) continue
Hardware watchpoint 1: *((uint32_t *)0x20001048)
Old value = 0x00000000
New value = 0xDEADBEEF
0x000102f4 in memset_bad (buf=0x20001000, val=0, len=256) at memutils.c:34
```

The corrupter is `memset_bad` overwriting 256 bytes starting at `0x20001000`, reaching `0x20001048`. The length argument is too large.

## Technique 2: Memory Protection in the ISS

Many ISS implementations let you define protected regions. Any access outside defined regions triggers an immediate stop:

```cpp
// Tell the ISS: RAM is 0x20000000–0x2000FFFF only
iss.add_region(0x20000000, 0x10000, READ | WRITE);
iss.add_region(0x00010000, 0x40000, READ | EXEC);
iss.add_region(0x40000000, 0x10000, READ | WRITE); // MMIO

// Any other access stops simulation and dumps state
iss.set_protection(STRICT);
```

This catches wild pointer writes that happen to land in unmapped space, which would be silent on real hardware.

## Technique 3: Stack Overflow Detection

Embed a canary at the bottom of the stack in your startup code:

```c
// startup.c
extern uint32_t __stack_limit;  // from linker script

void check_stack_canary(void) {
    if (*((volatile uint32_t *)&__stack_limit) != 0xDEADC0DE)
        fault_handler("Stack overflow detected!");
}
```

In the VP, you can also set a watchpoint on `__stack_limit` directly — the simulation stops the instant the stack overflows, not a few instructions later when something else crashes.

## Technique 4: Unaligned Access Detection

On ARM Cortex-M, unaligned accesses can be silently fixed in hardware or cause a fault depending on `CCR.UNALIGN_TRP`. In a VP, you can always log them:

```cpp
void Bus::b_transport(tlm::tlm_generic_payload& trans, sc_time& delay) {
    sc_dt::uint64 addr = trans.get_address();
    unsigned len  = trans.get_data_length();
    if ((addr % len) != 0) {
        SC_REPORT_WARNING("BUS", 
            ("Unaligned " + std::to_string(len*8) + "-bit access at 0x" 
             + to_hex(addr)).c_str());
    }
    // ... continue handling
}
```

## Technique 5: Logging Every Memory Access

When the bug is intermittent or the corruption address is unknown, enable full memory-access logging for a suspicious region:

```cpp
// VP model: intercept every access to SRAM
void Sram::b_transport(tlm::tlm_generic_payload& trans, sc_time& t) {
    if (verbosity >= 4) {
        auto cmd = trans.get_command() == tlm::TLM_WRITE_COMMAND ? "WR" : "RD";
        SC_REPORT_INFO("SRAM",
            (std::string(cmd) + " addr=0x" + to_hex(trans.get_address())
             + " len=" + std::to_string(trans.get_data_length())).c_str());
    }
    // handle transaction
}
```

Then grep the log for the first write to the corrupted address.

## Worked Example: Buffer Overflow

Symptom: the system crashes with a bad PC value (`0x00000003`) after calling `process_packet()`.

Register dump shows:
```
pc  = 0x00000003   ← invalid (not 4-byte aligned, not a valid code address)
lr  = 0xABCD1234   ← also garbage
sp  = 0x20001FF0   ← plausible
```

Hypothesis: the return address on the stack was overwritten. Set a watchpoint on the return address slot (`sp + 0` before the call) and rerun. The watchpoint fires inside `memcpy` which copies user data past the end of a 64-byte buffer into the stack frame. Classic stack-smashing.

Fix: add bounds check before memcpy. In the VP, confirm the fix by verifying the watchpoint no longer fires.

> **Interview answer:** "On a virtual prototype I use gdb watchpoints on the corrupted address to catch the exact faulting write, ISS memory protection to trap wild-pointer accesses immediately, and stack canaries with watchpoints to detect overflow at the moment it happens rather than at the eventual crash."
