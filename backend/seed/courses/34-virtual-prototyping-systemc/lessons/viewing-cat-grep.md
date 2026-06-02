# Viewing and Searching: cat, grep

Virtual prototype engineers spend a lot of time reading log files, simulation traces, and source code from the terminal. `cat` dumps file contents to the screen; `grep` filters those contents by pattern. Together they are the most-used duo for debugging build errors and simulation output.

---

## cat — Concatenate and Print

```bash
# Print a single file
cat sim.log

# Print multiple files in sequence (concatenate)
cat header.h body.cpp

# Show line numbers (-n)
cat -n initiator.cpp

# Show non-printing characters (-A) — useful to spot Windows CRLF line endings
cat -A Makefile
```

`cat` is short for "concatenate". Its original purpose is joining files; printing to the terminal is just a side effect of concatenating to standard output.

### When cat is not enough

For large files (thousands of lines of simulation trace), use `less` instead — it pages through the file without loading everything into memory:

```bash
less sim_output.vcd
# Navigate: Space = next page, b = back, /pattern = search, q = quit
```

**Common pitfall:** Running `cat` on a binary or a very large log file floods your terminal. Check file size with `ls -lh` first.

---

## grep — Global Regular Expression Print

`grep` searches for lines matching a pattern and prints them.

```bash
# Basic usage
grep "ERROR" sim.log

# Case-insensitive search (-i)
grep -i "warning" build.log

# Show line numbers (-n)
grep -n "sc_start" main.cpp

# Invert match — show lines that do NOT contain the pattern (-v)
grep -v "^#" Makefile     # Strip comment lines

# Count matching lines (-c)
grep -c "TLM_GENERIC_PAYLOAD" *.cpp

# Recursive search through all files in a directory (-r)
grep -r "b_transport" src/

# Print filename alongside each match (-H, default with -r)
grep -rH "OSCI" include/
```

### Useful grep flags table

| Flag | Effect |
|------|--------|
| `-i` | Case-insensitive |
| `-n` | Show line numbers |
| `-r` | Recursive through directories |
| `-l` | Print only filenames with matches |
| `-v` | Invert — lines without match |
| `-c` | Count matching lines |
| `-A N` | Show N lines After the match |
| `-B N` | Show N lines Before the match |
| `-C N` | Show N lines of Context (before + after) |

---

## Practical VP Debugging Patterns

### Find all SystemC errors in a log

```bash
grep -n "Error\|Fatal\|Abort" simulation.log
```

### Show context around a TLM error

```bash
grep -C 3 "TLM_INCOMPLETE_RESPONSE" sim.log
```

### Check which source files use a specific TLM phase

```bash
grep -rn "BEGIN_REQ\|END_RESP" src/
```

### Scan a Makefile for the SystemC include path

```bash
grep "SYSTEMC_HOME\|INC" Makefile
```

### Pipe cat into grep

```bash
cat *.log | grep "time="
# Equivalent (and more efficient):
grep "time=" *.log
```

---

## Worked Example — Tracking Down a Build Error

```bash
# Build fails; redirect stderr to a file
make 2>&1 | tee build.log

# Find the first error
grep -n "error:" build.log | head -5
# initiator.cpp:47: error: 'tlm::tlm_phase' was not declared in this scope

# See the 5 lines around line 47
grep -n "" initiator.cpp | sed -n '44,50p'
# Or use:
grep -n "tlm_phase\|#include" initiator.cpp
```

This pinpoints a missing `#include "tlm.h"` without opening an editor.

---

## Regular Expressions in grep

`grep` understands basic regular expressions by default. Use `-E` (or `egrep`) for extended regex:

```bash
# Lines starting with a digit
grep -E "^[0-9]" trace.log

# Lines containing "ns" or "ps"
grep -E "[0-9]+(ns|ps)" timing.log
```

> **Interview answer:** `cat` prints file contents to stdout; `grep` filters lines by pattern. Combining them with flags like `-n` (line numbers), `-r` (recursive), and `-C` (context) lets you locate errors in large simulation logs without opening a GUI editor.
