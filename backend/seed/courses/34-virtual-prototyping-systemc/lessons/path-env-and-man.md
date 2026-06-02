# PATH, Environment Variables, and man

SystemC and TLM toolchains depend heavily on environment variables: where the compiler is, where libraries live, and where headers are found. Understanding how the shell resolves commands and how to read documentation with `man` makes you self-sufficient in any Linux VP environment.

---

## What Is an Environment Variable?

An environment variable is a named string value that the shell passes to every process it starts. Programs read these variables at runtime to configure their behavior.

```bash
# Print a single variable
echo $HOME
# /home/tamer

# Print ALL environment variables
env

# Or use printenv
printenv PATH
```

---

## PATH — The Command Search Path

`PATH` is a colon-separated list of directories the shell searches when you type a command name.

```bash
echo $PATH
# /usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/opt/systemc/bin
```

When you type `g++`, the shell checks each directory in order until it finds an executable called `g++`. If none is found, you see `command not found`.

### Adding a directory to PATH

```bash
# Temporarily (current session only)
export PATH="$PATH:/opt/systemc-3.0/bin"

# Permanently — add to ~/.bashrc or ~/.bash_profile
echo 'export PATH="$PATH:/opt/systemc-3.0/bin"' >> ~/.bashrc
source ~/.bashrc    # Reload without restarting the shell
```

**Common pitfall:** Using `PATH=/new/dir` instead of `PATH="$PATH:/new/dir"` — this overwrites the existing PATH, breaking all standard commands.

---

## Key VP-Related Environment Variables

| Variable | Purpose |
|----------|---------|
| `SYSTEMC_HOME` | Root of SystemC installation |
| `TLM_HOME` | TLM 2.0 headers location |
| `LD_LIBRARY_PATH` | Where the dynamic linker searches for `.so` files |
| `CXX` | C++ compiler to use (`g++`, `clang++`) |
| `CXXFLAGS` | Compiler flags passed to every build |
| `MAKEFLAGS` | Default options for `make` |

```bash
# Typical VP setup in ~/.bashrc
export SYSTEMC_HOME=/opt/systemc-3.0
export TLM_HOME=$SYSTEMC_HOME/include/tlm
export LD_LIBRARY_PATH=$SYSTEMC_HOME/lib-linux64:$LD_LIBRARY_PATH
export CXX=g++
```

### Why LD_LIBRARY_PATH matters

When your compiled simulation binary runs, the OS dynamic linker must find `libsystemc.so`. If `LD_LIBRARY_PATH` does not include the library's directory, the simulation fails at startup:

```
./sim_top: error while loading shared libraries: libsystemc.so:
cannot open shared object file: No such file or directory
```

Fix:
```bash
export LD_LIBRARY_PATH=/opt/systemc-3.0/lib-linux64:$LD_LIBRARY_PATH
```

---

## Setting and Unsetting Variables

```bash
# Set a variable in the current shell only (no export = not inherited by child processes)
MY_SIM=run_001

# Export so child processes inherit it
export MY_SIM=run_001

# Unset a variable
unset MY_SIM

# Set temporarily for a single command
CXXFLAGS="-O2 -DDEBUG" make
```

---

## which and type — Locating Commands

```bash
# Find the path of an executable
which g++
# /usr/bin/g++

which systemc-config
# /opt/systemc-3.0/bin/systemc-config

# type shows how the shell resolves a name (alias, function, builtin, file)
type ls
# ls is aliased to 'ls --color=auto'
```

---

## man — The Manual

`man` opens the built-in reference manual for any command or system call.

```bash
man ls
man chmod
man grep
man gcc
man 2 open   # Section 2 = system calls
man 3 printf # Section 3 = C library functions
```

### Navigating inside man

| Key | Action |
|-----|--------|
| `Space` | Next page |
| `b` | Back one page |
| `/word` | Search forward |
| `n` | Next search result |
| `q` | Quit |

### Useful sections

| Section | Content |
|---------|---------|
| 1 | Shell commands |
| 2 | System calls (C) |
| 3 | Library functions (C/C++) |
| 5 | File formats |
| 8 | System administration |

```bash
# Quick one-line summary
whatis chmod
# chmod (1)  - change file mode bits

# Search man pages by keyword
man -k "shared library"
```

---

## Worked Example

```bash
# Check if SystemC is installed and where
which systemc-config 2>/dev/null || echo "Not in PATH"

# Add it and verify
export PATH="$PATH:/opt/systemc-3.0/bin"
systemc-config --version
# 3.0.0

# Check the library path is set
echo $LD_LIBRARY_PATH
# /opt/systemc-3.0/lib-linux64:

# Read the man page for make
man make   # Look up the -j flag for parallel jobs
```

> **Interview answer:** `PATH` is a colon-separated list of directories the shell searches for executables. `LD_LIBRARY_PATH` tells the dynamic linker where to find shared libraries. `export` makes a variable visible to child processes, and `man` opens the authoritative reference for any command.
