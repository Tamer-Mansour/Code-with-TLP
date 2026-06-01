# Bash Scripting Basics

A bash script automates a sequence of shell commands. Start every one with the same defensive header.

## The shebang + safety flags

```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
```

- `-e` — exit on any command failing.
- `-u` — error on referencing an unset variable.
- `-o pipefail` — pipeline fails if any step does (not just the last).
- `IFS=$'\n\t'` — split on newline and tab, not space (safer for filenames).

These four lines prevent half the bash bugs you'd ever write.

## Variables

```bash
name="Alice"
echo "$name"
echo "${name}"                   # same; braces let you do ${name}_suffix
echo "${name:-default}"          # default if unset
echo "${name:?Required}"         # error if unset
```

Always **quote variables** to handle spaces:

```bash
file="my file.txt"
rm "$file"                       # ✓
rm $file                         # ✗ tries to rm "my" then "file.txt"
```

## Command substitution

```bash
today=$(date +%F)
files=$(ls *.log)
count=$(grep -c error log)
```

Prefer `$(...)` over backticks — easier to nest.

## Conditionals

```bash
if [[ "$status" == "ok" ]]; then
    echo "good"
elif [[ "$status" =~ ^err ]]; then
    echo "error"
else
    echo "?"
fi

[[ -f file ]] && echo "exists"
[[ -d dir ]]  && echo "is directory"
[[ -z "$x" ]] && echo "empty"
[[ -n "$x" ]] && echo "non-empty"
```

`[[ ... ]]` is the bash-specific test (more features than `[ ... ]`). Use it.

## Loops

```bash
for file in *.log; do
    gzip "$file"
done

for i in {1..10}; do
    echo "$i"
done

for i in $(seq 1 10); do ...; done

while read -r line; do
    echo "got: $line"
done < input.txt

while true; do
    sleep 1
    echo tick
done
```

Use `read -r` to disable backslash interpretation.

## Functions

```bash
greet() {
    local name="${1:-world}"
    echo "hello, $name"
}

greet
greet "Alice"
```

`local` keeps variables scoped to the function. Without it, every variable is global — a frequent bug source.

## Arguments

```bash
$0      # script name
$1 $2   # first, second positional arg
$#      # number of args
$@      # all args, properly quoted
$*      # all args as one string

if [[ $# -lt 2 ]]; then
    echo "usage: $0 <input> <output>" >&2
    exit 2
fi
```

## Arrays

```bash
files=("a.txt" "b.txt" "c.txt")
echo "${files[0]}"
echo "${files[@]}"               # all
echo "${#files[@]}"              # count

for f in "${files[@]}"; do
    echo "$f"
done

# associative (bash 4+)
declare -A colors
colors[red]=#ff0000
colors[blue]=#0000ff
echo "${colors[red]}"
```

## Heredocs

```bash
cat <<EOF
Line 1
Line 2 with $variable interpolation
EOF

cat <<'EOF'
No interpolation here, $ is literal
EOF

# pass multi-line input to another command
ssh user@host <<'EOF'
    cd /opt/app
    ./deploy.sh
EOF
```

## Trap — cleanup on exit

```bash
tmpfile=$(mktemp)
trap 'rm -f "$tmpfile"' EXIT

# whatever you do, tmpfile gets deleted
```

`trap CMD EXIT` runs CMD when the script exits — for any reason. The RAII of bash.

## Don't ignore errors

```bash
some-command || echo "failed but continuing"
some-command || true              # explicit "I don't care"
some-command || { echo "fatal: x"; exit 1; }
```

When you do want to continue on error, make it explicit. Otherwise the `-e` flag will exit.

## When to switch to Python

Bash is great for: orchestrating shell commands, file manipulation, small CI scripts (< 100 lines).

Bash is painful for: anything involving math, JSON, HTTP, complex strings, structured data, real testing.

If your bash script has functions calling functions, a config file, or you find yourself parsing JSON with `awk` — rewrite in Python.

## shellcheck

`shellcheck` is a static analyzer for shell scripts. Run it on every script you write — catches dozens of common bugs (unquoted variables, wrong `[ ]`, etc.).

```bash
shellcheck deploy.sh
```

Integrate into CI. Never merge a script that doesn't pass shellcheck cleanly.
