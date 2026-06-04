# JWT Payload Decoder

JSON Web Tokens are the most widely used stateless authentication mechanism in Node.js APIs. Understanding their structure — and knowing how to decode them — is a core backend skill.

## JWT Structure

A JWT is three Base64URL-encoded segments separated by dots:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
.eyJzdWIiOiJ1c2VyXzEyMyIsInJvbGUiOiJhZG1pbiJ9
.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
  └── header ──┘  └──────── payload ─────────┘  └── signature ──┘
```

- **Header** — algorithm and token type (e.g. `{"alg":"HS256","typ":"JWT"}`)
- **Payload** — claims about the user and session
- **Signature** — HMAC or RSA signature for tamper detection

## Base64URL Encoding

Base64URL is a URL-safe variant of Base64:
- `+` is replaced with `-`
- `/` is replaced with `_`
- Padding `=` characters are omitted

To decode in Python:

```python
import base64, json

def base64url_decode(s):
    # Restore padding
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    # Swap URL-safe chars back
    s = s.replace("-", "+").replace("_", "/")
    return base64.b64decode(s)

jwt_token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyXzEifQ.sig"
payload_b64 = jwt_token.split(".")[1]
payload = json.loads(base64url_decode(payload_b64))
print(payload)  # {'sub': 'user_1'}
```

## Standard JWT Claims

| Claim | Meaning |
|-------|---------|
| `sub` | Subject — identifies the user |
| `iat` | Issued at — Unix timestamp |
| `exp` | Expiration — Unix timestamp |
| `iss` | Issuer — who created the token |
| `aud` | Audience — intended recipient |
| `role` | Custom claim — user role |
| `jti` | JWT ID — unique token identifier |

## Security Considerations

**Important:** The payload is only *encoded*, not *encrypted*. Anyone can decode a JWT without the secret key. Never put sensitive data (passwords, PII) in the payload.

The signature ensures the payload was not tampered with. Verification requires the secret key (or public key for RS256).

```js
// Server-side verification (Node.js with jsonwebtoken)
import jwt from "jsonwebtoken";

try {
  const payload = jwt.verify(token, process.env.JWT_SECRET);
  // payload.sub, payload.role are now trustworthy
} catch (err) {
  // Token is invalid, expired, or tampered
  res.status(401).json({ error: "Invalid token" });
}
```

## Common Security Mistakes

- **Never use `alg: none`** — this disables signature verification entirely
- **Store tokens in HttpOnly cookies**, not `localStorage` (XSS risk)
- **Always set `exp`** — tokens without expiry are permanent credentials
- **Verify the algorithm explicitly** — `jwt.verify(token, secret, { algorithms: ["HS256"] })`

## Further Reading

- **"Practical Node.js" by Azat Mardan** — https://github.com/azat-co/practicalnode — covers OAuth, sessions, and JWT-based authentication in production Node.js apps with Express.
- **"Become a Node.js Developer" by Thomas Gentilhomme** — https://fraxken.github.io/ebook_nodejs/ — covers security patterns and secrets management in Node.js.

## Exercise

In this exercise you will decode the payload segment of a JWT string and extract specific claims from it. You must implement the Base64URL decoding manually using only the Python standard library.
