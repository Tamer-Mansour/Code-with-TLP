# Managing Files: mkdir, cp, mv, rm

Once you can navigate the filesystem, the next skill is creating and manipulating files and directories. Virtual prototype projects can grow quickly — dozens of source files, build artifacts, and log outputs. These four commands keep things organized.

---

## mkdir — Make a Directory

```bash
# Create a single directory
mkdir build

# Create nested directories in one shot (-p = parents)
mkdir -p build/obj/initiator

# Create multiple directories at once
mkdir include src tests
```

**Why `-p` matters:** Without `-p`, `mkdir build/obj/initiator` fails if `build/` does not already exist. With `-p` it creates every missing level. This is standard in Makefiles.

```bash
# Inside a Makefile
$(shell mkdir -p $(BUILD_DIR)/obj)
```

---

## cp — Copy Files or Directories

```bash
# Copy a single file
cp main.cpp main_backup.cpp

# Copy a file to another directory
cp initiator.cpp backup/

# Copy a directory recursively (-r)
cp -r src/ src_backup/

# Preserve timestamps and permissions (-p)
cp -p sim_top sim_top.bak
```

| Flag | Meaning |
|------|---------|
| `-r` | Recursive (needed for directories) |
| `-p` | Preserve metadata (mode, ownership, timestamps) |
| `-v` | Verbose — print each file as it is copied |
| `-u` | Update — copy only when source is newer |

**Common pitfall:** `cp src dst` where `dst` is an existing directory copies the file *inside* that directory, not over it. Use `cp src dst/filename` if you want to rename it.

---

## mv — Move or Rename

```bash
# Rename a file
mv old_name.cpp new_name.cpp

# Move a file into a directory
mv initiator.cpp src/

# Move and rename simultaneously
mv tmp_result.log logs/run_001.log

# Move an entire directory
mv build/ build_old/
```

`mv` is how you rename files on Linux — there is no separate `rename` command in the POSIX core. It also works across directories as long as both are on the same filesystem; cross-filesystem moves copy then delete automatically.

**Common pitfall:** `mv file dir/` silently overwrites an existing file in `dir/` with the same name. Use `mv -n` (no-clobber) or `mv -i` (interactive) to be safe.

---

## rm — Remove Files

```bash
# Remove a single file
rm stale_log.txt

# Remove multiple files
rm *.o *.d

# Interactive prompt before each deletion (-i)
rm -i important_data.cpp

# Remove a directory and all its contents (-r)
rm -r build/

# Forceful removal, no prompts (-f)
rm -rf build/
```

> **Warning:** `rm -rf` is permanent. Linux has no recycle bin. A common VP workflow guard is to alias destructive commands:

```bash
alias rm='rm -i'
```

**Common pitfall:** Forgetting `-r` when deleting a directory — `rm build/` fails. You need `rm -r build/`.

---

## Worked Example — Setting Up a VP Project Structure

```bash
# Start fresh
mkdir -p tlm_demo/{include,src,tests,build/obj}

# Scaffold source files
cp ~/templates/sc_main.cpp tlm_demo/src/main.cpp
cp ~/templates/initiator.h  tlm_demo/include/

# Rename a template
mv tlm_demo/src/main.cpp tlm_demo/src/sc_top.cpp

# List the result
ls -R tlm_demo/
# tlm_demo/:
# build  include  src  tests
#
# tlm_demo/build:
# obj
#
# tlm_demo/include:
# initiator.h
#
# tlm_demo/src:
# sc_top.cpp
```

> **Interview answer:** `mkdir -p` creates directory trees, `cp -r` copies recursively, `mv` renames or relocates, and `rm -rf` removes everything — but with no undo, so always double-check the path before pressing Enter.
