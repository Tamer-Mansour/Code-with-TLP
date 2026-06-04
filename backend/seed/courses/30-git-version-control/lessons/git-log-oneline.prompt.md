# Simulate git log --oneline

## Problem

You are given a list of commit records, one per line, in the format:

```
<full_hash> <message>
```

Simulate the output of `git log --oneline` by printing only the **first 7 characters** of each hash followed by a space and the commit message. Commits are listed from newest (first line of input) to oldest (last line). Stop reading when you receive an empty line.

## Input

- One commit per line: `<40-char-hash> <message subject>`
- Terminated by an empty line

## Output

- One line per commit: `<7-char-hash> <message subject>`

## Example

**Input:**
```
a3f9d1e2b4c7f8910abc1234def56789ab123456 Add user authentication
b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c Fix login redirect bug
9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2b1c0 Initial commit

```

**Output:**
```
a3f9d1e Add user authentication
b1c2d3e Fix login redirect bug
9e8d7c6 Initial commit
```

## Constraints

- Hash will always be at least 7 characters long
- Message will not be empty
- At most 1000 commits per input
