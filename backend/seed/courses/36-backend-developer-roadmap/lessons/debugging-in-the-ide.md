# Debugging in the IDE

A debugger lets you pause a running program, inspect the state of every variable, step through code one line at a time, and understand exactly why a bug occurs — without adding a single `System.out.println`. This lesson covers the debugging workflow in **IntelliJ IDEA** (the most common IDE for Java), which maps closely to Eclipse and VS Code with the Language Support for Java extension.

## What Is a Breakpoint?

A **breakpoint** is a marker on a source line that tells the JVM to suspend execution there. Once suspended, you have full visibility into the call stack and all live variables.

To add a breakpoint in IntelliJ IDEA, click the gutter (left margin) to the left of a line number. A red circle appears. Press **Shift+F9** (or the bug icon) to start a **Debug** run instead of a normal run.

## A Concrete Example

Consider this class that has an off-by-one bug:

```java
public class SumCalculator {

    public static int sumUpTo(int n) {
        int total = 0;
        for (int i = 1; i < n; i++) {   // bug: should be i <= n
            total += i;
        }
        return total;
    }

    public static void main(String[] args) {
        System.out.println(sumUpTo(5)); // prints 10, but expected 15
    }
}
```

**Debugging steps:**

1. Click the gutter next to `int total = 0;` to set a breakpoint.
2. Press **Shift+F9** to start the debug session.
3. The program suspends. The Variables panel shows `n = 5`, `total = 0`.
4. Press **F8** (Step Over) repeatedly to advance one line at a time.
5. Watch the `i` variable — after the loop body runs with `i = 4`, the loop exits. You never see `i = 5`, revealing the `< n` vs `<= n` mistake.

Fix: change `i < n` to `i <= n`.

## Key Debugger Actions

| Action | IntelliJ shortcut | What it does |
|---|---|---|
| Step Over | F8 | Execute the current line; if it's a method call, don't enter it |
| Step Into | F7 | Enter the method call on the current line |
| Step Out | Shift+F8 | Run to the end of the current method and return to the caller |
| Resume | F9 | Continue running until the next breakpoint |
| Evaluate Expression | Alt+F8 | Type any Java expression and see its value right now |
| Toggle Breakpoint | Ctrl+F8 | Add or remove a breakpoint on the current line |

## Conditional Breakpoints

A regular breakpoint stops every time. A **conditional breakpoint** only stops when a boolean expression is true — essential when a bug only manifests on iteration 500 of a loop.

Right-click the red breakpoint circle and choose **Edit Breakpoint**, then enter a condition:

```java
// Only pause when i == 4
i == 4
```

The program runs at full speed and suspends only when the condition is satisfied.

## Watching Variables and the Call Stack

When execution is suspended, IntelliJ shows:

- **Variables panel** — all local variables and their current values in the current stack frame. You can expand objects to inspect fields.
- **Call stack (Frames) panel** — every method call that led to this point. Click any frame to switch context and inspect that method's locals.
- **Watches** — pin specific expressions (e.g., `total`, `list.size()`) that are re-evaluated after every step.

## Evaluate Expression

Press **Alt+F8** while paused to open the Evaluate dialog. You can run arbitrary Java code against the live heap:

```java
// In the Evaluate dialog while paused inside sumUpTo:
total + n            // see what the result would be
String.valueOf(n)    // call static methods
```

This is faster than adding temporary print statements and re-running.

## Common Mistakes

- **Running instead of debugging** — pressing **Shift+F10** starts a normal run; breakpoints are ignored. Always use **Shift+F9** for a debug run.
- **Breakpoint in unreachable code** — if the gutter icon turns grey with an X, the IDE cannot find bytecode for that line (usually a build problem). Do a full rebuild (`Build > Rebuild Project`).
- **Hot Code Replace** — IntelliJ can swap changed method bodies into a running debug session without restarting. This only works for method body changes; adding fields or methods requires a restart.
- **Relying only on print statements** — `System.out.println` debugging is slow and pollutes production code. Use the debugger first; add logging (SLF4J/Logback) for production diagnostics.

## Quick Debug Checklist

1. Set a breakpoint close to where the unexpected value first appears.
2. Start a debug run (Shift+F9).
3. Use Step Over to advance line by line, watching the Variables panel.
4. Use Step Into when you need to follow a method call deeper.
5. Use Evaluate (Alt+F8) to test hypotheses without modifying code.
6. Fix the bug, then remove or disable the breakpoint.

Mastering the debugger cuts the time you spend diagnosing bugs by an order of magnitude — use it as your first tool, not a last resort.
