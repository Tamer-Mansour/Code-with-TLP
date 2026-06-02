# Permissions and chmod

Every file on Linux has a permission set that controls who can read, write, or execute it. Build scripts that are not executable, libraries that are not readable, and directories that are not accessible are common tripping points in VP environments. Understanding permissions prevents hours of "permission denied" debugging.

---

## Reading Permission Strings

Run `ls -l` and examine the leftmost column:

```
-rwxr-xr--  1 tamer dev  512K Jun  1 10:22 sim_top
drwxr-x---  2 tamer dev  4.0K Jun  1 09:00 private_logs
lrwxrwxrwx  1 root  root    20 May 30 12:00 libsystemc.so -> libsystemc.so.3.0
```

The 10-character string breaks down as:

```
- r w x | r - x | r - -
│ ───── │ ───── │ ─────
│  user │ group │ other
└ type (- file, d dir, l symlink)
```

| Character | Meaning for files | Meaning for directories |
|-----------|-------------------|------------------------|
| `r` (4) | Read content | List contents |
| `w` (2) | Modify content | Create/delete entries |
| `x` (1) | Execute | Enter with `cd` |

---

## chmod — Change Mode

### Symbolic mode (readable)

```bash
# Add execute permission for the owner
chmod u+x build.sh

# Remove write permission for group and others
chmod go-w secret_config.h

# Set exact permissions: owner=rwx, group=r-x, others=r--
chmod u=rwx,g=rx,o=r sim_top
```

Symbols: `u` = user/owner, `g` = group, `o` = others, `a` = all three.

### Octal mode (concise)

Each permission group is represented as a 3-bit number:

| Octal | Binary | Permissions |
|-------|--------|-------------|
| 7 | 111 | rwx |
| 6 | 110 | rw- |
| 5 | 101 | r-x |
| 4 | 100 | r-- |
| 0 | 000 | --- |

```bash
# rwxr-xr-x — executable, others can read/run
chmod 755 sim_top

# rw-r--r-- — readable by all, writable only by owner
chmod 644 initiator.cpp

# rwx------ — private script
chmod 700 deploy.sh

# Apply recursively to a directory
chmod -R 755 build/
```

---

## Common VP Scenarios

### Build script not running

```bash
$ ./run_simulation.sh
bash: ./run_simulation.sh: Permission denied

$ ls -l run_simulation.sh
-rw-r--r-- 1 tamer dev 320 Jun 1 09:00 run_simulation.sh

# Fix: add execute bit
$ chmod +x run_simulation.sh
$ ./run_simulation.sh   # Now works
```

### Shared library not loadable

If `libsystemc.so` is in a directory without read permission for others, the dynamic linker will fail. Ensure library directories are at least `755`.

```bash
chmod 755 /opt/systemc-3.0/lib-linux64/
chmod 644 /opt/systemc-3.0/lib-linux64/libsystemc.so
```

### Lock down a private keyfile

```bash
chmod 600 ~/.ssh/id_rsa
# -rw------- Only the owner can read/write; ssh refuses to use it otherwise
```

---

## chown — Change Ownership (brief mention)

While `chmod` changes permissions, `chown` changes who owns the file:

```bash
# Change owner
sudo chown tamer initiator.cpp

# Change owner and group
sudo chown tamer:dev build/
```

Most permission issues in a single-user dev environment are solved with `chmod`, not `chown`.

---

## Checking Effective Permissions

```bash
# What can the current user do with this file?
ls -l sim_top

# Who am I?
whoami

# What groups am I in?
groups
```

---

## Quick Reference Table

| Use case | Command |
|----------|---------|
| Make a script executable | `chmod +x script.sh` |
| Public read-only file | `chmod 644 file` |
| Executable binary | `chmod 755 binary` |
| Private file | `chmod 600 file` |
| Lock down a directory | `chmod 700 dir/` |
| Recursive change | `chmod -R 755 dir/` |

> **Interview answer:** Linux permissions are three sets of read/write/execute bits for owner, group, and others. `chmod 755` makes a file executable by everyone but only writable by the owner — the standard permission for compiled binaries and shell scripts.
