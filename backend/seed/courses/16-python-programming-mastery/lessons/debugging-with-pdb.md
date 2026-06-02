# Debugging with pdb

`pdb` is Python's built-in interactive debugger. It lets you pause execution at any line, inspect variables, step through code, and evaluate expressions — all from the terminal, no IDE required.

## Starting the debugger

**Breakpoint in code (Python 3.7+):**

```python
def process(data):
    result = []
    for item in data:
        breakpoint()    # execution pauses here
        result.append(item * 2)
    return result
```

**Old-style (works everywhere):**

```python
import pdb; pdb.set_trace()
```

**Run a script under pdb from the start:**

```bash
python -m pdb my_script.py
```

## Core commands

| Command | Short | What it does |
|---------|-------|--------------|
| `next` | `n` | Execute current line, stay in this function |
| `step` | `s` | Step into a function call |
| `return` | `r` | Run until current function returns |
| `continue` | `c` | Resume until the next breakpoint |
| `quit` | `q` | Exit the debugger |
| `list` | `l` | Show source around current line |
| `where` | `w` | Print the call stack |
| `up` / `down` | `u`/`d` | Move up/down the call stack |
| `print expr` | `p expr` | Evaluate and print an expression |
| `pp expr` | `pp` | Pretty-print an expression |

Type any Python expression at the `(Pdb)` prompt to evaluate it immediately.

## Setting breakpoints from the prompt

```
(Pdb) break math_utils.py:15      # break at line 15
(Pdb) break add                   # break when function add is called
(Pdb) break 20, x > 0             # conditional breakpoint
(Pdb) tbreak 25                   # temporary — fires once then removes itself
(Pdb) clear 1                     # remove breakpoint #1
(Pdb) ignore 1 5                  # ignore breakpoint #1 for 5 hits
```

## Inspecting state

```
(Pdb) p result         # print variable
(Pdb) pp data          # pretty-print a long list/dict
(Pdb) len(result)      # any expression works
(Pdb) locals()         # all local variables
(Pdb) type(item)       # inspect types
```

## Post-mortem debugging

Run a script, let it crash, then inspect the crash site:

```bash
python -m pdb -c continue my_script.py
```

Or from the REPL after a crash:

```python
import pdb, traceback, sys

try:
    broken_function()
except Exception:
    pdb.post_mortem()  # opens debugger at the frame where exception was raised
```

## Common debugging workflow

1. Observe the symptom (wrong output, crash, hang).
2. Identify the area of code to investigate.
3. Add `breakpoint()` just before the suspicious code.
4. Run and inspect variables at the pause point.
5. Use `n` to step forward, `p var` to watch values change.
6. Remove the `breakpoint()` once fixed.

## Alternatives worth knowing

| Tool | When to use |
|------|-------------|
| `print()` | Quick sanity check; remove after |
| `logging.debug()` | Persistent diagnostic output in production code |
| `pdb` | Interactive exploration without an IDE |
| IDE debugger (VS Code, PyCharm) | GUI breakpoints, watch expressions, call-stack view |
| `icecream` (third-party) | Drop-in `print` replacement with context info |

`pdb` is most valuable when you have only a terminal (CI server, remote host, Docker container) and need to understand why code behaves unexpectedly.
