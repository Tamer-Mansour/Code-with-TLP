# Redis as a Session Store

HTTP is stateless. Every time a user makes a request your server needs to know who they are. The two main options are **cookie-based tokens** (JWT stored in the browser) and **server-side sessions** (a session ID in the cookie, session data on the server). Redis is the canonical backend for server-side sessions.

## Why Redis for sessions?

- **Speed**: sub-millisecond reads on every authenticated request.
- **TTL**: built-in expiry — sessions die automatically without a cron job.
- **Shared across replicas**: every app server reads from the same Redis, so sticky sessions are not required.
- **Atomic operations**: `HSET`/`HGETALL` in a single round trip; `EXPIRE` extends the TTL on activity.

## Data layout

Store each session as a Redis **hash** so you can update individual fields without reserializing the whole object.

```
Key:    session:<session_id>
Fields: user_id, email, role, created_at, last_seen
TTL:    30 min (extended on each request)
```

```python
import secrets, time
import redis

r = redis.Redis()
SESSION_TTL = 1800  # 30 minutes

def create_session(user_id: int, email: str, role: str) -> str:
    sid = secrets.token_hex(32)
    key = f"session:{sid}"
    r.hset(key, mapping={
        "user_id": user_id,
        "email": email,
        "role": role,
        "created_at": int(time.time()),
        "last_seen": int(time.time()),
    })
    r.expire(key, SESSION_TTL)
    return sid

def get_session(sid: str) -> dict | None:
    key = f"session:{sid}"
    data = r.hgetall(key)
    if not data:
        return None
    # Extend TTL on activity (sliding window)
    r.hset(key, "last_seen", int(time.time()))
    r.expire(key, SESSION_TTL)
    return {k.decode(): v.decode() for k, v in data.items()}

def delete_session(sid: str) -> None:
    r.delete(f"session:{sid}")
```

## Sliding vs absolute TTL

| Strategy | How it works | Use when |
|---|---|---|
| **Absolute TTL** | Session expires N minutes after creation | High-security apps (banking) |
| **Sliding TTL** | TTL resets on every request | Most web apps — keeps active users logged in |

For sliding TTL, call `EXPIRE session:<sid> <ttl>` on every authenticated request (or every N minutes to reduce Redis writes).

## Storing session IDs safely

Send the session ID in an `HttpOnly; Secure; SameSite=Strict` cookie. Never expose it in a URL or JS-accessible variable.

```http
Set-Cookie: sid=abc123; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=1800
```

## Concurrent sessions and device tracking

Store a set of active session IDs per user so you can show "active devices" or revoke all sessions on password change:

```python
# On session creation
r.sadd(f"user:{user_id}:sessions", sid)

# On password change: revoke all
def logout_all(user_id: int):
    sessions = r.smembers(f"user:{user_id}:sessions")
    for sid in sessions:
        r.delete(f"session:{sid.decode()}")
    r.delete(f"user:{user_id}:sessions")
```

## Session data size discipline

Keep sessions small. A session should hold identity and permission data, not a shopping cart or a user's full profile. The session ID unlocks a database query for anything heavier.

Typical session payload: 50–200 bytes per user. One million concurrent sessions ≈ 50–200 MB — very manageable in Redis.
