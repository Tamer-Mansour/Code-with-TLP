# Shell Basics and Navigation

The shell is the universal interface to Linux. Bash is the most common; zsh and fish are popular alternatives. The basics are identical.

## Where am I?

```bash
pwd                # print working directory
ls                 # list current dir
ls -la             # long, including hidden
ls -lh /var/log    # human-readable sizes
cd /tmp            # change dir
cd ~               # home
cd -               # previous directory
```

## Filesystem layout

```
/             root of everything
/home/<user>  user home dirs
/etc          system configs
/var          variable data (logs, caches, mail)
/usr          installed software, /usr/bin etc.
/bin /sbin    essential executables
/tmp          ephemeral, cleared on reboot
/proc /sys    kernel virtual filesystems
/dev          device files
/opt          optional manually-installed apps
/mnt /media   mount points
```

## Files

```bash
touch file.txt              # create empty file
cp src dst                  # copy
cp -r dir/ dst/             # recursive
mv old new                  # rename or move
rm file                     # delete
rm -rf dir/                 # recursive force (careful!)
mkdir -p path/to/dir        # create with parents
cat file                    # print contents
less file                   # paged viewer (q to quit)
head -20 file               # first 20 lines
tail -50 file               # last 50
tail -f log                 # follow as it grows
wc -l file                  # line count
```

## Wildcards and globs

```bash
ls *.txt                    # all .txt
ls /var/log/*.log
ls **/*.py                  # recursive (with globstar enabled)
rm temp_*                   # files starting with temp_
```

`?` matches one char, `*` matches any, `{a,b}` alternates.

## Pipes and redirection

```bash
cmd > file        # stdout to file (overwrite)
cmd >> file       # append
cmd < file        # stdin from file
cmd 2> err        # stderr to file
cmd > out 2>&1    # combine
cmd1 | cmd2       # pipe stdout to next stdin
cmd1 |& cmd2      # also stderr
```

```bash
ps aux | grep nginx | wc -l
journalctl -u my-service | tail -100
```

## Variables and environment

```bash
NAME=Alice                  # local
export NAME=Alice           # also export to subprocesses
echo $NAME
echo "$NAME"                # quote to prevent splitting

env                         # all env vars
$HOME $PATH $USER
```

## Command help

```bash
man ls                # manual page
ls --help
which python          # path to executable
type cd               # alias / function / builtin
```

## History

```bash
history
!42                   # rerun line 42
!!                    # rerun last
!grep                 # rerun last grep command
Ctrl-R                # reverse-i-search
```

## A few productivity tips

- `Ctrl-A` / `Ctrl-E` — beginning / end of line.
- `Ctrl-W` — delete word back.
- `Ctrl-L` — clear screen.
- `Tab` — complete files, commands, args.
- `alias ll='ls -la'` — short names for common commands.

Put aliases and exports in `~/.bashrc` (or `~/.zshrc`) so they persist.
