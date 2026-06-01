# grep, sed, awk

Three classic Unix text-processing tools. Knowing them well makes you 10× faster on the command line.

## grep — search

```bash
grep error /var/log/syslog
grep -i error log                   # case insensitive
grep -r TODO src/                    # recursive
grep -v error log                    # invert (lines NOT matching)
grep -c error log                    # count matches
grep -n error log                    # line numbers
grep -A 3 -B 1 error log             # 3 lines after, 1 before
grep -l error logs/*                 # filenames only

# extended regex (POSIX)
grep -E 'error|warn|fail' log

# perl-compatible regex
grep -P '\d{4}-\d{2}-\d{2}' log

# print only matched part
grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' log    # IPs
```

For huge codebases, use **ripgrep** (`rg`) instead — vastly faster, respects `.gitignore`:

```bash
rg --type py "TODO"
rg "func.*Handle" src/
```

## sed — substitute

```bash
sed 's/old/new/' file              # first match per line
sed 's/old/new/g' file             # global per line
sed 's/old/new/gi' file            # global + insensitive
sed -i 's/old/new/g' file          # in-place edit

sed -n '5,10p' file                # print lines 5-10
sed '/^$/d' file                   # delete empty lines
sed -e 's/foo/X/' -e 's/bar/Y/'    # multiple commands

# use different delimiter when content has /
sed 's|/usr/local|/opt|g' file
```

In-place is dangerous — back up first or use `-i.bak`:

```bash
sed -i.bak 's/old/new/g' file      # also creates file.bak
```

## awk — column-aware

awk treats each line as fields separated by whitespace (or custom):

```bash
ps aux | awk '{ print $1, $11 }'           # user and command
df -h | awk '$5 > "80%" { print $6 }'      # mountpoints over 80% full
ls -l | awk '{ s += $5 } END { print s }'  # sum file sizes

awk -F: '{ print $1 }' /etc/passwd         # custom delimiter (colon)
awk -F',' 'NR > 1 { print $2 }' data.csv   # skip header, print col 2

# multiple actions
awk '
  /error/ { errors++ }
  /warn/  { warns++ }
  END { print "errors:", errors, "warns:", warns }
' log
```

awk is a real programming language — variables, arrays, regex, functions. For one-liners, `awk '{print $N}'` covers 80% of usage.

## Pipelines

```bash
# top 10 IPs in an access log
cat access.log | awk '{print $1}' | sort | uniq -c | sort -rn | head

# count error types
grep ERROR app.log | awk '{print $4}' | sort | uniq -c | sort -rn

# disk usage of subdirectories, sorted
du -sh */ | sort -h
```

`sort | uniq -c | sort -rn` is the canonical "count occurrences" idiom.

## cut, paste, tr, head, tail

```bash
cut -d, -f1,3 data.csv             # columns 1 and 3
cut -c1-10 file                    # first 10 chars per line
tr 'a-z' 'A-Z' < file              # uppercase
tr -d '\r' < windows.txt           # delete carriage returns
paste -d, a.txt b.txt              # zip files side-by-side
head -20 file
tail -50 file
```

## xargs — feed lines to a command

```bash
find . -name "*.tmp" | xargs rm
echo "1 2 3" | xargs -n 1 echo line:
ls *.png | xargs -P 4 -I {} convert {} {}.thumb.png
```

`-P N` runs N in parallel. Mighty for batch processing.

## When to write Python instead

For anything involving stateful counting, JSON, or complex logic across many lines, write a Python script. Pipelines are excellent at line-oriented transformations; they become unreadable when you bolt on too much logic.

A short loop in Python with `for line in sys.stdin:` beats a 300-character pipeline almost every time.
