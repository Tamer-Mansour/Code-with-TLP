# Permissions and Ownership

Every file has an **owner**, a **group**, and **permissions** for owner / group / everyone else.

## Reading `ls -l`

```
-rwxr-xr-x  1 alice staff 1234 Jun 1 10:00 script.sh
│└┬┘└┬┘└┬┘  │ └──┬┘└─┬─┘
│ │  │  │   │    │   └ size in bytes
│ │  │  │   │    └ group
│ │  │  │   └ owner
│ │  │  │
│ │  │  └ "others" (everyone else): r-x = read, execute
│ │  └ "group": r-x
│ └ "owner": rwx = read, write, execute
└ type: - file, d directory, l link, c char dev, b block dev
```

## chmod

Octal form — each digit is `r=4 + w=2 + x=1`:

```bash
chmod 755 script.sh        # rwxr-xr-x
chmod 644 readme.md        # rw-r--r--
chmod 600 secret.key       # rw------- (owner only)
chmod 700 .ssh             # owner only, all perms
chmod 750 deploy.sh        # owner rwx, group rx, others nothing
```

Symbolic form:

```bash
chmod +x script.sh         # add execute for all
chmod u+x script.sh        # only user (owner)
chmod g+w file             # group can write
chmod o-rwx file           # remove all perms from others
chmod a+r file             # all read
```

## Common patterns

| Octal | Used for                                     |
|-------|----------------------------------------------|
| 755   | Executable scripts, directories you traverse |
| 644   | Regular files                                |
| 600   | Private files (SSH private keys, .env)       |
| 700   | Private dirs (`~/.ssh`, `~/.gnupg`)          |
| 666   | World-writable (almost always wrong)         |
| 777   | World-writable+executable (almost certainly wrong) |

## Directories

For directories:

- **r** — list contents (`ls`)
- **w** — create/delete files inside
- **x** — traverse / `cd` into it; required to use anything inside

A directory you can read but not execute lets you see the names but not the files. A directory you can execute but not read lets you reach known children without listing.

## chown / chgrp

```bash
sudo chown alice file
sudo chown alice:staff file        # owner + group
sudo chown -R deploy /var/www      # recursive
sudo chgrp dev /etc/myapp
```

You need root to change ownership (unless giving away your own files).

## umask — default permissions

```bash
umask                              # show current
umask 022                          # default — new files 644, new dirs 755
umask 077                          # private — new files 600, new dirs 700
```

Set in `~/.bashrc` for per-user policy.

## Special bits

- **setuid (4xxx)** — file runs with owner's privileges. `passwd` uses this.
- **setgid (2xxx)** — file runs with group's; on a directory, new files inherit the directory's group.
- **sticky (1xxx)** — on a dir, only owner can delete files (used by `/tmp`).

```bash
chmod 4755 sudo                    # setuid + 755
chmod 2775 shared-dir              # setgid for shared workspace
chmod 1777 /tmp                    # sticky
ls -l                              # 's' replaces 'x' in display
```

## ACLs (when standard perms aren't enough)

```bash
setfacl -m u:bob:rwx file          # give Bob rwx specifically
setfacl -m g:dev:r-- file
getfacl file
```

POSIX ACLs let you grant per-user or per-group permissions on top of the standard model. Usually overkill — well-designed groups are cleaner.

## Common mistakes

- `chmod 777` to "fix permissions" — almost always wrong. Find the actual missing permission.
- Setting executable bit on data files — not harmful, but confusing.
- Forgetting that **directory traversal needs `x`** — files inside an unreadable directory can be unreachable even if the file itself is readable.
- World-writable `~/.ssh/authorized_keys` — SSH refuses to use it (security feature).
