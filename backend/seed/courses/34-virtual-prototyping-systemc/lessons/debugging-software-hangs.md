# Debugging Software Hangs and Deadlocks

A hang — where the software stops making visible progress — is one of the most frustrating bugs to diagnose because there is no crash, no error message, and no clear starting point. On a virtual prototype, a hang is actually easier to debug than on real hardware because simulation time is deterministic and you can pause execution at any moment.

## Types of Hangs

| Type | Cause | Telltale sign |
|---|---|---|
| Polling spin | Peripheral bit never set | Single PC repeating in trace |
| Deadlock | Two mutexes locked in opposite order | Two tasks, neither progressing |
| Interrupt starvation | IRQ disabled but software waiting for it | `cpsr.I = 1` while polling |
| WFI with no wakeup | CPU in Wait-For-Interrupt but no IRQ pending | ISS shows WFI instruction; time stops |
| Livelock | Two threads continuously preempting each other | Two PCs alternating at high frequency |

## Step 1: Pause and Inspect

The first move on a hung VP is always the same:

```
Ctrl-C   (in gdb, or kill -SIGINT to the VP process)

(gdb) info registers
(gdb) backtrace
(gdb) x/10i $pc
```

This tells you *where* the CPU stopped. If `bt` shows `uart_poll -> main`, the CPU is spinning inside `uart_poll`. That is your starting point.

## Step 2: Check the Interrupt State

Interrupts disabled while waiting for a peripheral is the most common hang cause in bare-metal code:

```
(gdb) p/x $cpsr
$1 = 0x600000D3
```

Decode bit 7 (I-bit):
```
0xD3 = 1101 0011
         ^
         bit 7 = 1 → IRQ disabled!
```

The software disabled interrupts (e.g., inside a critical section) and never re-enabled them. The peripheral interrupt will never fire.

## Step 3: Check the Peripheral Register

Use gdb to read the peripheral register the software is polling:

```
(gdb) x/1wx 0x40010000
0x40010000:    0x00000000
```

If the hardware model never sets the ready bit, there are two possibilities:
1. The model is buggy (did not implement the register).
2. The peripheral was never correctly initialized (e.g., clock not enabled).

Check the initialization sequence in the trace:

```bash
grep "0x40010000" trace.log | head -20
```

If no write to the control register appears before the poll, the driver never started the peripheral.

## Step 4: Identify Spin-Loop Boundaries

Extract the PC column from the trace and find the loop:

```bash
awk '{print $2}' trace.log | uniq -d | head -10
```

Or look for the longest run of identical PCs:

```bash
awk '{print $2}' trace.log | uniq -c | sort -rn | head -5
```

Example output:
```
 999982 0x000100a0
 999981 0x000100a4
 999980 0x000100a8
```

Three addresses dominating the trace: a tight polling loop.

## Step 5: Deadlock Detection in RTOS Scenarios

With an RTOS, multiple tasks may be involved. Pause the simulation and examine each task's stack:

```
(gdb) info threads
  Id  Target Id  Frame
* 1   Thread 1   mutex_lock (m=0x20001000) at mutex.c:45
  2   Thread 2   mutex_lock (m=0x20002000) at mutex.c:45
```

Thread 1 holds mutex A and waits for mutex B. Thread 2 holds mutex B and waits for mutex A. Classic deadlock.

On a VP, you can inspect the mutex data structures directly:

```
(gdb) p *(Mutex *)0x20001000
$2 = {owner = 2, waiters = {1}}
(gdb) p *(Mutex *)0x20002000
$3 = {owner = 1, waiters = {2}}
```

## Injecting a Stimulus to Break the Hang

Sometimes you want to confirm the hypothesis without modifying the binary. Use gdb to write the ready bit directly:

```
(gdb) set *((volatile uint32_t *)0x40010000) = 0x00000001
(gdb) continue
```

If the software now proceeds, the peripheral model is definitively missing that flag. This is a quick way to distinguish "software logic bug" from "model bug" without recompiling anything.

## Common Pitfalls

- **Confusing WFI with a hang.** If the CPU is in `WFI` (Wait For Interrupt) and a timer interrupt fires regularly, that is not a hang. Check whether simulation time is advancing.
- **Assuming the hang is in the last function called.** The stack trace shows where the CPU is *now*, but it may have been in a different function when the hang was triggered (e.g., interrupt handler corrupted state).
- **Not checking sc_time_stamp().** In a multi-process SystemC simulation, one process might be blocked while others run. Confirm the *simulation* time is not advancing, not just the wall clock.

> **Interview answer:** "I pause execution with Ctrl-C, read the PC and CPSR to find the spin location and check if interrupts are enabled, then read the peripheral register being polled to determine if the model or the driver initialization is at fault."
