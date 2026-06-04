# IPv4 Address Validator

Every device on the internet has an IP address. This exercise applies string parsing and validation logic to IPv4 addresses — the same validation that routers, firewalls, and web servers perform every time data crosses a network.

## What You Will Practice

- Splitting strings with `.split()`
- Validating numeric ranges with conditionals
- Handling edge cases (leading zeros, wrong part count, non-numeric parts)
- Reading from stdin until EOF

## IPv4 Format

An IPv4 address looks like `192.168.1.1`:
- Four **octets** (groups), separated by dots
- Each octet is a decimal integer from 0 to 255
- No leading zeros allowed (so `01` is invalid, `0` is valid)

## Approach

```python
import sys

def is_valid_ipv4(s):
    parts = s.split('.')
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():       # must be all digits
            return False
        if len(part) > 1 and part[0] == '0':   # no leading zeros
            return False
        if not (0 <= int(part) <= 255):
            return False
    return True

for line in sys.stdin:
    line = line.strip()
    if line:
        print('VALID' if is_valid_ipv4(line) else 'INVALID')
```

Notice how `part.isdigit()` correctly rejects empty strings and strings with `+` or `-` signs, while the leading-zero check handles `01` through `09`.
