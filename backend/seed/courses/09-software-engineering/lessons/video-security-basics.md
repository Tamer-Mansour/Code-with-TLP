# Video: Web Security for Developers — OWASP Top 10

This video tours the OWASP Top 10 web application security risks, showing each vulnerability with a live exploit demonstration in a deliberately insecure application, then walking through the correct fix. Aimed squarely at developers rather than penetration testers.

**Key takeaways:**
- SQL Injection and how parameterized queries and ORMs eliminate the risk entirely — with a side-by-side comparison of vulnerable and safe code.
- Broken Authentication: password hashing (bcrypt, Argon2), session fixation, and secure cookie attributes (`HttpOnly`, `Secure`, `SameSite`).
- Cross-Site Scripting (XSS): reflected vs. stored vs. DOM-based XSS, output encoding, and Content Security Policy headers.
- Insecure Direct Object References (IDOR): why you must authorize every request, not just authenticate the user.
- Secrets management: why environment variables beat hardcoded strings, and how secrets managers (AWS Secrets Manager, HashiCorp Vault) keep credentials out of your source code and logs.
