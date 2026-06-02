# Finding Files with find

`grep` searches inside files. `find` searches for files themselves — by name, type, size, age, or permissions. In a large VP project with dozens of subdirectories, `find` is how you locate a stray header, confirm that all object files were built, or clean up temporary artifacts.

---

## Basic Syntax

```bash
find <path> <options> <expression>
```

- `<path>` — Where to start searching (`.` means current directory)
- `<options>` — Control depth, follow symlinks, etc.
- `<expression>` — Predicates that filter results (`-name`, `-type`, `-size`, …)

---

## Finding by Name

```bash
# Exact name (case-sensitive)
find . -name "Makefile"

# Wildcard — all .cpp files
find . -name "*.cpp"

# Case-insensitive name match
find . -iname "readme*"

# Find in a specific directory only
find /opt/systemc -name "*.h"
```

**Common pitfall:** The glob pattern must be quoted. Without quotes the shell expands `*.cpp` before `find` sees it, giving unexpected results.

```bash
# Wrong — shell expands *.cpp first
find . -name *.cpp

# Correct
find . -name "*.cpp"
```

---

## Finding by Type

| Flag | Matches |
|------|---------|
| `-type f` | Regular files |
| `-type d` | Directories |
| `-type l` | Symbolic links |

```bash
# List all directories under build/
find build/ -type d

# List all symbolic links in /usr/local/lib
find /usr/local/lib -type l
```

---

## Finding by Age

```bash
# Modified less than 1 day ago
find . -mtime -1

# Modified more than 7 days ago (good for cleanup)
find . -mtime +7 -name "*.log"

# Modified in the last 30 minutes
find . -mmin -30
```

---

## Finding by Size

```bash
# Files larger than 10 MB
find . -size +10M

# Files smaller than 1 KB (likely empty or stubs)
find . -size -1k -type f
```

---

## Executing Commands on Results

The `-exec` flag runs a command on every match. `{}` is a placeholder for the found path; `\;` terminates the command.

```bash
# Print details of every .o file
find build/ -name "*.o" -exec ls -lh {} \;

# Delete all stale object files
find build/ -name "*.o" -exec rm {} \;

# Batch delete (more efficient — passes all paths at once)
find build/ -name "*.o" -delete

# Run file on every binary to confirm it is ELF
find . -type f -executable -exec file {} \;
```

---

## Combining Predicates

```bash
# .cpp files modified today that are larger than 5 KB
find src/ -name "*.cpp" -mtime -1 -size +5k

# Either .cpp or .h files
find . \( -name "*.cpp" -o -name "*.h" \)

# .log files NOT named "reference.log"
find . -name "*.log" ! -name "reference.log"
```

---

## Limiting Depth

```bash
# Search only one level deep
find . -maxdepth 1 -name "*.md"

# Start from level 2 downward
find . -mindepth 2 -name "Makefile"
```

---

## Worked Example — VP Project Housekeeping

```bash
# 1. Find all object files left from a failed build
find . -name "*.o" -type f
# ./build/obj/initiator.o
# ./build/obj/target.o

# 2. Delete them all
find . -name "*.o" -delete

# 3. Find every Makefile in the project tree
find . -name "Makefile" -type f

# 4. Locate the SystemC shared library on the system
find /usr /opt -name "libsystemc*" -type f 2>/dev/null
# /opt/systemc-3.0/lib-linux64/libsystemc.so

# 5. Find simulation logs older than a week and archive them
find logs/ -name "*.log" -mtime +7 -exec gzip {} \;
```

---

## find vs. grep — When to Use Which

| Goal | Tool |
|------|------|
| Locate a file by name | `find` |
| Search inside files for text | `grep` |
| Locate then search inside | `find … -exec grep … {} \;` |

```bash
# Find every .cpp file that mentions sc_module
find src/ -name "*.cpp" -exec grep -l "sc_module" {} \;
```

> **Interview answer:** `find` searches the filesystem by metadata — name, type, size, age. Key flags are `-name` for patterns, `-type f/d` for file/directory, `-mtime` for age, and `-exec` to act on results. Always quote glob patterns to prevent shell expansion.
