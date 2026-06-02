# Navigating the Filesystem: pwd, ls, cd

Every SystemC build script, Makefile, and simulation binary lives somewhere in a directory tree. Before you can compile or run anything, you need to move around that tree confidently. Three commands handle 90 % of filesystem navigation: `pwd`, `ls`, and `cd`.

---

## pwd — Where Am I?

`pwd` prints the **present working directory** — the full absolute path of the directory your shell is currently sitting in.

```bash
$ pwd
/home/tamer/vp_workspace/tlm2_examples
```

This is your reference point. Every relative path you type is interpreted from here.

**Why it matters for VP work:** SystemC and TLM libraries are often installed in non-standard locations (`/opt/systemc`, `/usr/local/lib`). When a `make` command fails with "file not found", the first thing to check is whether you are in the right directory.

---

## ls — What Is Here?

`ls` lists the contents of a directory.

| Flag | Effect |
|------|--------|
| `-l` | Long format — permissions, owner, size, timestamp |
| `-a` | Show hidden files (names starting with `.`) |
| `-h` | Human-readable file sizes (KB, MB) |
| `-R` | Recursive — list subdirectories too |
| `--color` | Highlight file types (usually on by default) |

```bash
$ ls -lh
total 48K
drwxr-xr-x 3 tamer tamer 4.0K May 30 09:12 include
drwxr-xr-x 2 tamer tamer 4.0K May 30 09:13 src
-rw-r--r-- 1 tamer tamer  18K May 30 09:14 Makefile
-rwxr-xr-x 1 tamer tamer 512K May 30 09:20 sim_top
```

Notice the first character of each permission string: `d` means directory, `-` means regular file, `l` means symbolic link.

**Common pitfall:** Running `ls` and not seeing your compiled binary. Check `ls -la` — it may be in a sub-folder (`build/`, `obj/`) defined by the Makefile.

---

## cd — Change Directory

`cd` moves you to another directory.

```bash
# Absolute path — always works regardless of where you are
cd /opt/systemc-3.0/examples/tlm

# Relative path — relative to pwd
cd src/initiator

# Go up one level
cd ..

# Go up two levels
cd ../..

# Go to your home directory (shortcut)
cd ~

# Go back to the previous directory (very useful!)
cd -
```

### Practical VP workflow

```bash
# Start at project root
cd ~/vp_workspace/tlm_bus_example

# Check what is there
ls -l

# Enter the source directory
cd src

# Confirm location
pwd
# /home/tamer/vp_workspace/tlm_bus_example/src

# Jump back to project root
cd -
# /home/tamer/vp_workspace/tlm_bus_example
```

---

## Tab Completion — Your Best Friend

Press `Tab` after typing a partial path and the shell completes it for you. Press `Tab` twice to see all matches when there is ambiguity. This prevents typos in long SystemC library paths like `/opt/systemc-3.0.0/lib-linux64/`.

---

## Putting It Together

```bash
$ pwd
/home/tamer

$ cd vp_workspace/tlm_bus_example
$ ls -lh include/ src/
include/:
-rw-r--r-- 1 tamer tamer 2.1K initiator.h
-rw-r--r-- 1 tamer tamer 1.8K target.h

src/:
-rw-r--r-- 1 tamer tamer 4.3K initiator.cpp
-rw-r--r-- 1 tamer tamer 3.7K target.cpp
-rw-r--r-- 1 tamer tamer  890 main.cpp
```

> **Interview answer:** `pwd` prints your current directory, `ls` lists its contents, `cd` moves you to another directory. Together they let you orient yourself in a project tree before running build commands.
