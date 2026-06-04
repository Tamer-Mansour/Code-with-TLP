# JWT Payload Decoder

JSON Web Tokens (JWTs) consist of three Base64URL-encoded parts separated by dots: `HEADER.PAYLOAD.SIGNATURE`. The payload contains JSON claims about the user.

Given a JWT string, decode the payload and extract specific claims.

## Base64URL Decoding

Base64URL differs from standard Base64:
- `-` replaces `+`
- `_` replaces `/`
- Padding `=` characters are omitted (you must restore them before decoding)

Restore padding by adding `=` until the string length is a multiple of 4 (add 0, 1, or 2 `=` characters as needed).

## Input Format

- Line 1: the JWT string (three dot-separated segments)
- Line 2: integer `Q` — the number of claims to extract
- Next `Q` lines: one claim key per line

## Output Format

For each claim key, output one line: `key: value`

- String values are printed without quotes
- Number and boolean values are printed as-is
- If the key is not present in the payload, print `key: MISSING`

## Example

**Input:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyXzEyMyIsInJvbGUiOiJhZG1pbiIsImlhdCI6MTcwMDAwMDAwMCwiZXhwIjoxNzAwMDg2NDAwfQ.signature_ignored
4
sub
role
exp
name
```

**Output:**
```
sub: user_123
role: admin
exp: 1700086400
name: MISSING
```

## Notes

- You only need to decode the **second segment** (payload). The signature is not verified.
- Use only the Python standard library (`base64`, `json`).
- Boolean values in JSON (`true`/`false`) become Python `True`/`False`; print them as `True` or `False`.

## Constraints

- 1 ≤ Q ≤ 20
- The JWT payload is always valid JSON
- Claim keys are non-empty strings without spaces
