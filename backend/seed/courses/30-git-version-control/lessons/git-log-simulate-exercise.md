# Exercise: Simulate git log --oneline

Every time you run `git log --oneline`, Git takes the full 40-character SHA-1 hash stored in each commit object and abbreviates it to the first 7 characters — enough to be unique in virtually any repository. The output then pairs that short hash with the single-line subject of the commit message.

## What you are building

You will write a program that reads a list of raw commit records and reproduces the `git log --oneline` output format. This exercise reinforces your understanding of how Git stores commits and how the abbreviated hash system works.

## Why this matters

Understanding `git log` is fundamental to navigating any repository. The `--oneline` flag is the most-used log format in day-to-day development — it fits more information on screen and is the format you'll see referenced in pull-request reviews, bug reports, and CI pipelines.

## Input format

Each line of input has the form:

```
<full_40_char_hash> <commit message subject>
```

Commits are listed from **newest to oldest** (as Git outputs them). Input ends when you receive an empty line.

## Output format

For each commit, print:

```
<first_7_chars_of_hash> <commit message subject>
```

## Example

Input:
```
a3f9d1e2b4c7f8910abc1234def56789ab123456 Add user authentication
b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c Fix login redirect bug
9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2b1c0 Initial commit
```

Output:
```
a3f9d1e Add user authentication
b1c2d3e Fix login redirect bug
9e8d7c6 Initial commit
```

## Further reading

- *Pro Git* (Chapter 2 — Git Basics): https://git-scm.com/book/en/v2/Git-Basics-Viewing-the-Commit-History
- Atlassian Git Tutorials — git log: https://www.atlassian.com/git/tutorials/git-log
