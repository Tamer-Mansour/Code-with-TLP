# rwx to Octal Permissions

Convert Unix-style permission strings to 3-digit octal.

## Input

Zero or more lines. Each line is a 9-character permission string using `r`, `w`, `x`, `-`.

Example:

```
rwxr-xr-x
rw-r--r--
rwxrwxrwx
```

## Output

For each input line, print the 3-digit octal equivalent on its own line.

`r=4, w=2, x=1` per triple, summed.

## Examples

Input:

```
rwxr-xr-x
rw-r--r--
rwxrwxrwx
```

Output:

```
755
644
777
```

Input:

```
---------
```

Output:

```
000
```

Input:

```
rwx------
r--r--r--
-w-r-x-w-
```

Output:

```
700
444
252
```

## Notes

- Each input line is exactly 9 characters long (when non-empty).
- Empty input → no output.
- Whitespace-only lines should be ignored.
