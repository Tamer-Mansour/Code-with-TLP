# sudo and ssh: Privilege and Remote Access

Virtual prototype development often involves two realities: installing system-wide tools that require root access, and running simulations on a remote build server. `sudo` handles privilege escalation; `ssh` handles the secure remote connection.

---

## sudo — Superuser Do

`sudo` runs a single command with the privileges of another user — usually root (UID 0). It is safer than logging in as root because:

- Actions are logged (audit trail in `/var/log/auth.log`)
- You only elevate for the exact command that needs it
- Your password is required (confirming identity)

```bash
# Install a package
sudo apt install libboost-dev

# Copy a file to a system directory
sudo cp libsystemc.so /usr/local/lib/

# Edit a system configuration file
sudo nano /etc/ld.so.conf.d/systemc.conf

# Run as a different user
sudo -u builder make install

# Open a root shell (use sparingly)
sudo -i
# or
sudo su
```

### sudo in VP workflows

```bash
# Install SystemC system-wide after building from source
sudo make install DESTDIR=/opt/systemc-3.0

# Refresh the dynamic linker cache after adding a library
sudo ldconfig

# Grant a teammate access to a shared simulation directory
sudo chmod -R g+rw /srv/simulations
```

**Common pitfall:** Running the entire build process with `sudo`. Build artifacts then become owned by root, and subsequent normal-user builds fail with "permission denied". Only use `sudo` for the specific step that needs root.

---

## /etc/sudoers — Who Can Use sudo

The file `/etc/sudoers` defines which users may run which commands as root. Never edit it directly — use `visudo`:

```bash
sudo visudo
```

A typical line:
```
tamer ALL=(ALL) NOPASSWD: /usr/bin/make
```

This lets user `tamer` run `make` as root without a password prompt — useful in automated CI pipelines.

---

## ssh — Secure Shell

`ssh` opens an encrypted remote terminal session. VP teams routinely run long simulations on dedicated servers with many cores; `ssh` is how you get there.

```bash
# Basic login
ssh tamer@192.168.1.77

# Login with a specific key file
ssh -i ~/.ssh/server77_rsa tamer@192.168.1.77

# Run a single command remotely (no interactive shell)
ssh tamer@192.168.1.77 "cd /builds/tlm_demo && make -j8"

# Copy files to a remote host (scp)
scp initiator.cpp tamer@192.168.1.77:/home/tamer/vp_project/src/

# Copy recursively
scp -r src/ tamer@192.168.1.77:/home/tamer/vp_project/

# Copy from remote to local
scp tamer@192.168.1.77:/builds/logs/sim.log ./local_logs/
```

---

## SSH Key-Based Authentication

Passwords over SSH are inconvenient in scripts. Key-based auth is faster and more secure.

```bash
# 1. Generate a key pair (public + private)
ssh-keygen -t ed25519 -C "tamer@workstation"
# Creates:
#   ~/.ssh/id_ed25519       (private — keep secret, chmod 600)
#   ~/.ssh/id_ed25519.pub   (public — safe to share)

# 2. Copy the public key to the server
ssh-copy-id tamer@192.168.1.77
# (or manually append ~/.ssh/id_ed25519.pub to ~/.ssh/authorized_keys on the server)

# 3. Now login without a password
ssh tamer@192.168.1.77
```

**Critical:** The private key file must have permission `600`. SSH will refuse to use it otherwise:
```bash
chmod 600 ~/.ssh/id_ed25519
```

---

## ~/.ssh/config — Aliases for Servers

Avoid typing long hostnames and options by creating a config file:

```
# ~/.ssh/config
Host build77
    HostName 192.168.1.77
    User tamer
    IdentityFile ~/.ssh/server77_rsa
    Port 22
```

Now connect with just:
```bash
ssh build77
scp src/ build77:/home/tamer/vp_project/
```

---

## Running Long Simulations Remotely

A simulation that takes hours will die if the SSH connection drops. Use `tmux` or `nohup` to detach it:

```bash
# Using nohup
ssh build77 "nohup ./sim_top > sim.log 2>&1 &"

# Using tmux (preferred — lets you reattach later)
ssh build77
tmux new -s sim_session
./sim_top
# Ctrl+B then D to detach; reattach later with: tmux attach -t sim_session
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `sudo cmd` | Run cmd as root |
| `sudo -i` | Open a root shell |
| `ssh user@host` | Remote terminal |
| `scp file user@host:path` | Copy file to remote |
| `scp user@host:file .` | Copy file from remote |
| `ssh-keygen` | Generate key pair |
| `ssh-copy-id host` | Install public key on server |

> **Interview answer:** `sudo` runs a single command with root privileges and logs the action — safer than a root shell. `ssh` provides an encrypted terminal to a remote host; combined with key-based auth and `~/.ssh/config` aliases, it makes remote VP build servers feel like local machines.
