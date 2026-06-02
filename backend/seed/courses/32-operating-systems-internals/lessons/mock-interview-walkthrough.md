# Mock Interview Walkthrough: A Complete System Trace

This lesson presents a full mock interview scenario — the kind of question asked at companies that build operating systems, embedded firmware, or silicon. Work through the answer yourself before reading the model response. The goal is to practice connecting every layer of the stack in a single coherent narrative.

## The Question

> "You are debugging a new SoC running Linux. The system boots, but after a few seconds the watchdog resets the board. The UART shows the kernel timer interrupt fires at the expected rate. Your only debug tool is a virtual prototype of the same SoC. Walk me through exactly how you would isolate the root cause."

Take two minutes to outline your approach before reading on.

---

## Model Answer: Step-by-Step

### 1. Reproduce the failure on the virtual prototype

```bash
qemu-system-riscv64 -M virt -kernel vmlinux \
    -dtb board.dtb -nographic -s -S
```

Reproduce the watchdog reset in the simulator. Confirm it triggers at the same point (same uptime, same kernel log output). If it does not reproduce, the bug is timing- or hardware-specific — a different investigation path.

### 2. Enable instruction and interrupt tracing

```bash
qemu-system-riscv64 ... -d int,cpu_reset 2>trace.log
```

Watch for:
- The watchdog interrupt being raised.
- Any unhandled exceptions (`mcause` values) just before reset.
- Whether the CPU enters an infinite loop (repeating PC in trace).

### 3. Set a GDB breakpoint at the watchdog kick site

The watchdog is "kicked" (reset) by writing to its service register. If the kick stops happening, the thread responsible has either crashed or is starved.

```bash
(gdb) target remote :1234
(gdb) b watchdog_keepalive      # or watchdog_ping
(gdb) commands 1
   silent
   printf "WDT kick at %s\n", $pc
   continue
end
(gdb) c
```

If the breakpoint stops firing before the reset, the kicking thread is stuck.

### 4. Identify what the kicking thread is blocked on

When the watchdog kick stops, break into the debugger:

```
(gdb) interrupt
(gdb) thread apply all bt      # print backtrace for every kernel thread
```

Look for the watchdog thread's stack. Common culprits:

| Stack frame seen | Likely cause |
|---|---|
| `__schedule` → `io_schedule` | Thread blocked waiting for I/O |
| `down_read` / `mutex_lock` | Thread blocked on a lock |
| Tight loop at one PC | Software deadlock or infinite loop |
| Stack pointer in wrong range | Stack overflow |

### 5. Trace the lock contention

If the thread is spinning on a lock, find the lock holder:

```bash
(gdb) p *(&some_spinlock)      # inspect lock state
(gdb) p lock->owner            # which task holds it?
```

On a virtual prototype you can add a watchpoint on the lock word and log every acquire/release:

```cpp
// In the spinlock model
void spin_lock(spinlock_t *lock) {
    TRACE("spinlock acquire attempt at 0x%p from PC=0x%lx", lock, get_caller_pc());
    // … existing logic
}
```

### 6. Confirm with MMIO watchpoint on watchdog registers

Set a watchpoint on the watchdog service register address to see exactly when the last kick occurred and what instruction performed it:

```
(gdb) watch *(uint32_t*)0x10010000   # watchdog service reg
(gdb) c
(gdb) # fires every kick; note the time; stop after last kick
```

### 7. Root cause and fix

In this scenario the root cause is: a driver's interrupt handler acquires a mutex (illegal from interrupt context), which deadlocks with the watchdog thread that holds the same mutex. The watchdog thread sleeps waiting for the mutex to be released, the kick stops, the hardware watchdog fires.

**Fix:** replace the mutex with a spinlock in the interrupt handler, or defer work to a kernel thread using a workqueue.

> **Interview answer:** I reproduce on the virtual prototype, enable interrupt and instruction traces, use GDB to confirm when watchdog kicks stop firing, print all thread backtraces to find the blocked kicking thread, identify the held lock, trace contention with MMIO watchpoints, and determine the deadlock root cause — all without touching real hardware.

## Key Interview Signals This Answer Demonstrates

- **Systematic debugging** — not guessing; hypothesis → evidence at each step.
- **Tool fluency** — QEMU flags, GDB remote target, watchpoints, thread backtraces.
- **OS internals knowledge** — mutex vs. spinlock, interrupt context rules, watchdog driver architecture.
- **Virtual prototype literacy** — knows how to use the simulator as a debugging tool, not just a platform.
- **Communication** — narrates the approach clearly before diving into commands.

## Practice Scenarios

Try the same structured walkthrough for:
1. A process segfaults on first memory access after `mmap`.
2. The kernel OOM killer fires unexpectedly under moderate load.
3. A SPI driver reads all-zeros after switching clock polarity.
4. A secondary CPU hart never comes online after SMP boot.

Each of these is a real bring-up bug class you will encounter in production.
