# Exercise: Classify Diff Lines

Version control systems and code review tools display differences between file versions as unified diffs. In this exercise you will parse a simplified diff format and count the added, removed, and unchanged lines.

## Unified Diff Format (Simplified)

Each line in the diff starts with a single character:
- `+` — added line (present in new version, not in old)
- `-` — removed line (present in old version, not in new)
- ` ` (space) — context line (unchanged, present in both versions)
- Lines starting with `@` or `---` or `+++` are diff headers — ignore them

## Input

Multiple lines of a simplified diff.

## Output

Three lines in this exact format:
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
