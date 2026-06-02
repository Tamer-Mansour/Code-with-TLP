# HTTP Status Code Classifier

You are given **N** HTTP status codes (integers), one per line. For each code, print one line:

```
<code> <category>
```

Where `<category>` is determined by the first digit:

| First digit | Category |
|-------------|----------|
| 1 | Informational |
| 2 | Success |
| 3 | Redirection |
| 4 | Client Error |
| 5 | Server Error |

## Input format

```
N
code1
code2
...
codeN
```

## Output format

One line per code: `<code> <category>`

## Example

Input:
```
4
200
404
301
500
```

Output:
```
200 Success
404 Client Error
301 Redirection
500 Server Error
```
