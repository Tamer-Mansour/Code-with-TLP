# Environment Variables

Environment variables are key-value pairs available to every process in a shell session. They configure program behavior without hard-coding values — essential for portability, security, and twelve-factor app design.

## Reading and setting variables

```bash
echo $HOME              # print a variable
echo $PATH              # colon-separated search path for executables
echo $USER              # current user
echo $SHELL             # current shell binary

# Set a local variable (current shell only; NOT exported to children)
MY_VAR=hello
echo $MY_VAR

# Export to child processes
export MY_VAR=hello
export DB_HOST=db.prod.example.com
export DB_PORT=5432

# Set for a single command only
DB_HOST=localhost python3 app.py

env                     # print all environment variables
printenv HOME           # print one variable
```

## PATH — how commands are found

When you type `python3`, the shell searches each directory in `$PATH` left-to-right for an executable named `python3`.

```bash
echo $PATH
# /usr/local/bin:/usr/bin:/bin:/usr/local/sbin:/usr/sbin

# Add a directory to PATH (for this session)
export PATH="$HOME/.local/bin:$PATH"

# Check which binary will be used
which python3
type python3
```

## Persisting variables

| File             | When sourced           | Typical use               |
|------------------|------------------------|---------------------------|
| `~/.bashrc`      | Every interactive bash | Aliases, PATH additions   |
| `~/.bash_profile`| Login shells only      | ENV vars for login        |
| `~/.profile`     | Login shells (POSIX)   | Portable env vars         |
| `/etc/environment`| All users, system-wide | System-wide env vars      |
| `/etc/profile.d/*.sh`| Login shells, all users | System-wide additions |

```bash
# Add to ~/.bashrc for a permanent alias + export
echo 'export EDITOR=vim' >> ~/.bashrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc     # reload immediately
```

## .env files

Applications often read a `.env` file at startup:

```bash
# .env
DATABASE_URL=postgres://user:pass@localhost:5432/mydb
SECRET_KEY=supersecret
DEBUG=false
```

```python
# Python — load with python-dotenv
from dotenv import load_dotenv
import os
load_dotenv()
db = os.environ["DATABASE_URL"]
```

**Never commit `.env` files to version control.** Add them to `.gitignore`. Secrets in environment variables are far safer than secrets hard-coded in source files.

## systemd service environment

For services managed by systemd, set environment variables in the unit file:

```ini
[Service]
Environment="DB_HOST=localhost"
Environment="DB_PORT=5432"
EnvironmentFile=/etc/myapp/env   # read from a file
ExecStart=/usr/local/bin/myapp
```

## Variable substitution and defaults

```bash
echo ${MY_VAR:-default}     # use "default" if MY_VAR is unset or empty
echo ${MY_VAR:=default}     # also assign the default to MY_VAR
echo ${MY_VAR:?error msg}   # fail with message if unset

# Substring
x="Hello World"
echo ${x:6}         # World
echo ${x:0:5}       # Hello
echo ${x/World/Linux}  # Hello Linux
```

## Security considerations

- Avoid putting secrets in environment variables in contexts where they could appear in logs (some frameworks log all env vars at startup).
- For production secrets, prefer a secrets manager (HashiCorp Vault, AWS Secrets Manager, etc.) that injects values at runtime without storing them in files or env vars.
- Use `unset MY_VAR` to remove a variable from the current shell's environment.
