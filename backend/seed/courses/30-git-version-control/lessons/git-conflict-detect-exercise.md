# Exercise: Detect Merge Conflicts

When Git cannot automatically reconcile two branches — because both branches modified the same lines in the same file — it writes **conflict markers** directly into the affected file and halts the merge. The developer must then open the file, decide what the correct content should be, remove the markers, and complete the merge.

## Conflict marker anatomy

```
<<<<<<< HEAD
your version of the code
=======
their version of the code
>>>>>>> feature-branch
```

- `<<<<<<<` marks the **start** of a conflict block (your current branch's content follows)
- `=======` is the **divider** separating the two versions
- `>>>>>>>` marks the **end** of a conflict block (the incoming branch's content precedes it)

A file can contain many conflict blocks if multiple sections were changed on both branches.

## What you are building

Write a program that reads the contents of a file that may contain conflict markers and reports how many conflict blocks it found.

## Why this matters

Automated tooling (linters, CI checks, pre-commit hooks) routinely scan files for unresolved conflict markers before allowing a build or deployment to proceed. This is a real pattern used in professional pipelines.

## Input format

Lines of text that may or may not contain conflict marker lines. The input represents a file that was left in a conflict state.

## Output format

```
Conflicts: N
```

where `N` is the number of conflict blocks found. Each block begins with a line **starting with** `<<<<<<<`.

## Example

Input:
```
def greet():
<<<<<<< HEAD
    return 'Hello, world'
=======
    return 'Hi there'
>>>>>>> feature-branch

def farewell():
<<<<<<< HEAD
    return 'Goodbye'
=======
    return 'See you later'
>>>>>>> feature-branch
```

Output:
```
Conflicts: 2
```

## Further reading

- *Pro Git* — Basic Merge Conflicts: https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging#_basic_merge_conflicts
- Atlassian — resolving merge conflicts: https://www.atlassian.com/git/tutorials/using-branches/merge-conflicts
