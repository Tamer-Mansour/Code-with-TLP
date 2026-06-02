# The A Extension: Atomics and LR/SC

The RISC-V "A" standard extension adds **atomic memory operations** — instructions that perform a read-modify-write on a memory location as an indivisible unit, visible to all cores simultaneously. These are the hardware primitives on which all lock-free data structures, mutexes, and concurrent algorithms are built.

## Why Atomics Are Necessary

Consider a shared counter incremented by two threads simultaneously:

```c
// Thread A and Thread B both execute:
counter++;
```

Without hardware atomics, the compiled load-add-store sequence has a race:

```
Thread A: LW x1, 0(x10)    → x1 = 5
Thread B: LW x1, 0(x10)    → x1 = 5
Thread A: ADDI x1, x1, 1   → x1 = 6
Thread B: ADDI x1, x1, 1   → x1 = 6
Thread A: SW x1, 0(x10)    → mem = 6
Thread B: SW x1, 0(x10)    → mem = 6  (should be 7!)
```

The A extension solves this with instructions that cannot be interleaved.

## LR/SC: Load-Reserved / Store-Conditional

This pair implements **optimistic concurrency** (also called LL/SC in MIPS):

- `LR.W` / `LR.D`: Loads a value and places a **reservation** on the memory address.
- `SC.W` / `SC.D`: Stores a value only if the reservation is still valid. Returns 0 on success, non-zero on failure.

```asm
# Atomic increment of word at address in x10
retry:
    lr.w   x5, (x10)        # load-reserved: x5 = *x10, set reservation
    addi   x5, x5, 1        # x5 = x5 + 1
    sc.w   x6, x5, (x10)    # store-conditional: *x10 = x5 if reservation held
    bnez   x6, retry        # if SC failed (x6 != 0), try again
```

The reservation is invalidated if:
- Another hart writes to the same address.
- A context switch occurs.
- (Implementation-defined) other memory operations occur.

LR/SC is more flexible than compare-and-swap (CAS) — it can express any read-modify-write without a fixed comparison value.

## AMO: Atomic Memory Operations

AMO instructions perform a single-instruction read-modify-write:

| Instruction | Operation |
|---|---|
| `AMOADD.W` | `mem = mem + rs2`, returns old `mem` |
| `AMOSWAP.W` | `mem = rs2`, returns old `mem` |
| `AMOAND.W` | `mem = mem & rs2` |
| `AMOOR.W` | `mem = mem \| rs2` |
| `AMOXOR.W` | `mem = mem ^ rs2` |
| `AMOMIN.W` | `mem = min(mem, rs2)` (signed) |
| `AMOMAX.W` | `mem = max(mem, rs2)` (signed) |
| `AMOMINU.W` | `mem = min(mem, rs2)` (unsigned) |
| `AMOMAXU.W` | `mem = max(mem, rs2)` (unsigned) |

Doubleword variants (`.D`) exist for RV64. Each AMO atomically reads the old value, computes the operation, writes the result back.

```asm
# Atomically add 1 to word at x10, result in x11
li      x12, 1
amoadd.w  x11, x12, (x10)   # x11 = old *x10; *x10 = old + 1
```

## Ordering Suffixes: .AQ and .RL

AMO and LR/SC instructions optionally carry ordering bits:

| Suffix | Meaning |
|---|---|
| (none) | Unordered — no extra ordering |
| `.aq` | Acquire — no subsequent accesses reordered before this |
| `.rl` | Release — no preceding accesses reordered after this |
| `.aqrl` | Both — full sequentially consistent operation |

```asm
amoswap.w.aq   x5, x6, (x10)    # acquire: use to take a lock
amoswap.w.rl   x0, x0, (x10)    # release: use to release a lock (write 0)
```

## Implementing a Mutex

```asm
# Lock: atomically set *lock from 0 to 1
# x10 = address of lock
lock:
    li      x11, 1
    amoswap.w.aq  x12, x11, (x10)   # x12 = old value; *lock = 1
    bnez    x12, lock                 # if old != 0, someone held lock → retry

# Unlock: store 0 with release ordering
    amoswap.w.rl  x0, x0, (x10)     # *lock = 0, release ordering
```

## Common Pitfall

Using AMO instructions without `.aq`/`.rl` suffixes in lock implementations leads to reordering bugs under RVWMO. Always annotate atomic operations with the appropriate ordering. The C11/C++11 atomics (`std::atomic`) map directly to these suffixes.

> **Interview answer:** RISC-V's A extension provides two atomic mechanisms: LR/SC (load-reserved/store-conditional) for flexible optimistic read-modify-write loops, and AMO instructions for single-instruction atomic operations like add, swap, and compare. The `.aq` and `.rl` suffixes embed acquire/release memory ordering directly into the instruction.
