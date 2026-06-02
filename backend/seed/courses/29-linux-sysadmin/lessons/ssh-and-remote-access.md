# SSH and Remote Access

**SSH (Secure Shell)** is the standard protocol for encrypted remote terminal sessions and file transfers on Linux. Almost every production server is managed exclusively over SSH.

## Connecting

```bash
ssh user@host                         # basic connect
ssh -p 2222 user@host                 # non-standard port
ssh -i ~/.ssh/my_key.pem user@host    # specify private key
ssh -v user@host                      # verbose (debug connection issues)
```

When you connect for the first time, SSH shows the server's fingerprint and adds it to `~/.ssh/known_hosts`. If the fingerprint changes unexpectedly, SSH warns you — this is a security protection against man-in-the-middle attacks.

## Key-based authentication

Passwords are convenient but weaker than keys. Key pairs consist of:

- **Private key** — stored on your machine, never shared.
- **Public key** — placed on the server.

```bash
# Generate a key pair (Ed25519 is the modern choice)
ssh-keygen -t ed25519 -C "your@email.com"

# Copy your public key to a server
ssh-copy-id user@host

# Manually: append to the server's authorized_keys
cat ~/.ssh/id_ed25519.pub | ssh user@host "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

The `~/.ssh` directory and `authorized_keys` file must have strict permissions:

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

## SSH config file

Put connection settings in `~/.ssh/config` to avoid typing them every time:

```
Host myserver
    HostName 203.0.113.45
    User ubuntu
    IdentityFile ~/.ssh/myserver_key
    Port 22

Host bastion
    HostName 203.0.113.1
    User ec2-user
    ForwardAgent yes
```

Now `ssh myserver` works without any flags.

## Server-side configuration

The SSH daemon is configured in `/etc/ssh/sshd_config`. Key hardening options:

| Setting                      | Recommended value | Why                             |
|------------------------------|-------------------|---------------------------------|
| `PasswordAuthentication`     | `no`              | Keys only                       |
| `PermitRootLogin`            | `no`              | Use a normal user + sudo        |
| `AllowUsers` / `AllowGroups` | your users        | Explicit allow list             |
| `Port`                       | non-standard      | Reduces noise in logs           |

After editing, reload the daemon:

```bash
sudo systemctl reload sshd
```

## File transfer

```bash
# Copy a local file to a remote server
scp report.txt user@host:/home/user/

# Copy from remote to local
scp user@host:/var/log/app.log ./

# Recursive directory copy
scp -r ./dist/ user@host:/var/www/html/

# rsync (incremental, faster for large trees)
rsync -avz ./build/ user@host:/var/www/html/
rsync -avz --delete ./build/ user@host:/var/www/html/   # delete remote extras
```

## SSH tunnels

Tunnels forward a port through an encrypted connection:

```bash
# Local forward: connect to remote DB through SSH
ssh -L 5433:localhost:5432 user@host
# Now psql -h localhost -p 5433 connects to the remote Postgres

# Dynamic SOCKS proxy (browser through your server)
ssh -D 1080 user@host

# Remote forward: expose a local service on a remote port
ssh -R 8080:localhost:3000 user@host
```

## Troubleshooting

- `Permission denied (publickey)` — check `~/.ssh/authorized_keys` on the server; check permissions.
- `Host key verification failed` — the server fingerprint changed. If expected, remove the old entry: `ssh-keygen -R hostname`.
- `Connection timed out` — firewall is blocking port 22; check `ufw` or cloud security groups.
