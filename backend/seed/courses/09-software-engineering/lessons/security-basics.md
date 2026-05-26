# Security Basics for Software Engineers

Security is not a feature you add at the end — it is a quality attribute that must be designed in from the start. Retrofitting security into an existing system is orders of magnitude more expensive than building it in correctly. This lesson covers the security fundamentals every software engineer must understand, regardless of specialisation.

## OWASP Top 10

The Open Web Application Security Project (OWASP) publishes a list of the ten most critical web application security risks, updated periodically based on real-world breach data.

### A01: Broken Access Control

The most critical risk as of OWASP 2021. Access control enforces that users can only access what they are authorised to access.

```python
# VULNERABLE: user can access any order by guessing its ID
@app.get("/orders/{order_id}")
def get_order(order_id: int, current_user: User = Depends(get_current_user)):
    return db.query(Order).get(order_id)   # no ownership check!

# FIXED: verify the order belongs to the requesting user
@app.get("/orders/{order_id}")
def get_order(order_id: int, current_user: User = Depends(get_current_user)):
    order = db.query(Order).get(order_id)
    if order is None or order.user_id != current_user.id:
        raise HTTPException(status_code=404)   # 404, not 403, to avoid ID enumeration
    return order
```

### A02: Cryptographic Failures

Sensitive data exposed because it was stored or transmitted without proper encryption.

```python
# WRONG: never store plaintext passwords
user.password = "super_secret_123"

# WRONG: MD5 and SHA-1 are broken for passwords (too fast, susceptible to rainbow tables)
import hashlib
user.password = hashlib.md5(password.encode()).hexdigest()

# CORRECT: use a proper password hashing algorithm with a work factor
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)   # bcrypt with default cost=12, salted automatically

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

Also: always use HTTPS (TLS 1.2+) in production. Never store secrets in environment variables in code — use a secrets manager (AWS Secrets Manager, HashiCorp Vault).

### A03: Injection

Injection attacks occur when untrusted data is sent to an interpreter as part of a command or query.

**SQL Injection:**

```python
# VULNERABLE: user input concatenated directly into SQL
def get_user(username: str):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    # Input "'; DROP TABLE users; --" would execute!
    return db.execute(query)

# FIXED: parameterised query — the database driver handles escaping
def get_user(username: str):
    return db.execute(
        "SELECT * FROM users WHERE username = :username",
        {"username": username}
    )
    # With SQLAlchemy ORM (even safer):
    # return db.query(User).filter(User.username == username).first()
```

**Command Injection:**

```python
import subprocess
import shlex

# VULNERABLE
def convert_image(filename: str):
    os.system(f"convert {filename} output.png")   # filename could be "x; rm -rf /"

# FIXED: use a list of arguments (never passes input through a shell)
def convert_image(filename: str):
    subprocess.run(["convert", filename, "output.png"], check=True)
```

### A04: Insecure Design

Security problems that arise from missing or ineffective control design — not from implementation bugs.

Example: A password reset flow that uses a predictable token (`reset_token = str(user.id)`) can be exploited to reset any user's password. Secure design requires cryptographically random, time-limited, single-use tokens:

```python
import secrets
import hashlib
from datetime import datetime, timedelta

def create_reset_token(user: User, db) -> str:
    raw_token = secrets.token_urlsafe(32)   # 256 bits of entropy
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    
    db.execute(
        "INSERT INTO password_reset_tokens (user_id, token_hash, expires_at) "
        "VALUES (:user_id, :token_hash, :expires_at)",
        {
            "user_id": user.id,
            "token_hash": token_hash,
            "expires_at": datetime.utcnow() + timedelta(hours=1),
        }
    )
    return raw_token   # send to user by email; only hash stored in DB
```

### A07: Identification and Authentication Failures

- Weak or reused passwords allowed
- No brute-force protection on login endpoints
- Session tokens not invalidated on logout
- Sensitive operations don't require re-authentication

```python
# Rate limiting login attempts (using a sliding window counter in Redis)
import redis
from fastapi import HTTPException

r = redis.Redis()

def check_login_rate_limit(ip: str) -> None:
    key = f"login_attempts:{ip}"
    attempts = r.incr(key)
    if attempts == 1:
        r.expire(key, 900)   # 15-minute window
    if attempts > 10:
        raise HTTPException(
            status_code=429,
            detail="Too many login attempts. Try again in 15 minutes."
        )
```

## Input Validation

All input from the outside world (query parameters, request bodies, file uploads, HTTP headers) must be validated before use.

```python
from pydantic import BaseModel, EmailStr, constr, validator

class UserRegistrationRequest(BaseModel):
    email: EmailStr                                    # validates email format
    username: constr(min_length=3, max_length=30,      # enforces length + pattern
                     pattern=r'^[a-zA-Z0-9_]+$')
    password: constr(min_length=12)                    # minimum length

    @validator('password')
    def password_complexity(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
```

Validate file uploads: check MIME type (not just extension), maximum size, scan for malware if user-uploaded content is served to other users.

## Secrets Management

**Never hardcode secrets in source code.** This includes development secrets.

```python
# WRONG — never do this, even in dev
DATABASE_URL = "postgresql://admin:password123@localhost/myapp"
STRIPE_SECRET_KEY = "sk_live_abc123..."

# WRONG — .env files should not be committed
# (even if .gitignore is set, accidents happen)

# CORRECT — use environment variables injected at runtime
import os
DATABASE_URL = os.environ["DATABASE_URL"]   # raises if not set — fail fast

# BETTER for production — use a secrets manager
import boto3
def get_secret(secret_name: str) -> str:
    client = boto3.client("secretsmanager", region_name="eu-west-1")
    return client.get_secret_value(SecretId=secret_name)["SecretString"]
```

Git pre-commit hooks (e.g., `detect-secrets`, `trufflehog`) can scan commits for accidentally committed secrets and block them before they reach the remote.

## Security in Code Review

Every PR review should include a security check:

- [ ] Is user input validated before use?
- [ ] Are SQL queries parameterised (no string concatenation)?
- [ ] Are secrets or credentials present anywhere in the diff?
- [ ] Are authorisation checks present for all data-modifying endpoints?
- [ ] Is user-generated content sanitised before display (XSS prevention)?
- [ ] Are error messages leaking internal details (stack traces, file paths, SQL)?
- [ ] Are new dependencies checked for known vulnerabilities? (`pip audit`, `npm audit`)

## Dependency Security

Your code is only as secure as its dependencies. A vulnerability in a dependency you didn't write can compromise your system.

```bash
# Python: check installed packages for known CVEs
pip install pip-audit
pip-audit

# Output:
# Package    Version  ID             Fix Versions
# ---------- -------- -------------- ------------
# requests   2.27.1   GHSA-j8r2-6x86 2.28.2

# Node.js
npm audit
npm audit fix   # automatically update vulnerable deps where safe
```

Keep dependencies up to date. Subscribe to security advisories for critical dependencies. Use Dependabot (GitHub) or Renovate to automate dependency update PRs.

## The Principle of Least Privilege

Every component, user, and service should have only the permissions it needs to do its job — nothing more.

- Database users: your application's DB user should have `SELECT, INSERT, UPDATE, DELETE` on its tables only — not `DROP TABLE`, `CREATE USER`, or access to other databases
- IAM roles: a Lambda function that reads from S3 should have `s3:GetObject` on the specific bucket, not `s3:*` on `*`
- API tokens: use scoped tokens with minimum permissions; rotate them regularly

Security is everyone's responsibility on an engineering team. A single developer who commits a hardcoded API key or skips an auth check can undo the security work of the entire team.
