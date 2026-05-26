# Classify Diff Lines

Parse lines from a unified diff format and count the added, removed, and unchanged (context) lines.

## Line Classification

- Lines starting with `+` (but NOT `+++`): **added**
- Lines starting with `-` (but NOT `---`): **removed**
- Lines starting with a space ` `: **unchanged**
- All other lines (`@`, `+++`, `---`, empty): **ignore**

## Input

Lines of a unified diff on standard input.

## Output

Exactly three lines:
```
added: <count>
removed: <count>
unchanged: <count>
```

## Example

**Input:**
```
--- a/auth.py
+++ b/auth.py
@@ -10,7 +10,8 @@
 def login(user, password):
-    return check(user, password)
+    if not user:
+        return None
+    return verify(user, password)
 
 def logout(user):
```

**Output:**
```
added: 3
removed: 1
unchanged: 3
```

## Important

- `+++` is a diff header, NOT an added line — do not count it
- `---` is a diff header, NOT a removed line — do not count it
- The blank line in the diff (` `) — a line with just a space — counts as unchanged
