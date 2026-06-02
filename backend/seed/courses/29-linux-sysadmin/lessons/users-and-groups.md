# Users and Groups

Linux enforces access control through **users** and **groups**. Every process, file, and socket has an owner. Understanding user management is essential for any system administrator.

## Key files

| File                  | Purpose                                      |
|-----------------------|----------------------------------------------|
| `/etc/passwd`         | User accounts (name, UID, home, shell)        |
| `/etc/shadow`         | Hashed passwords (root-readable only)         |
| `/etc/group`          | Group definitions and members                 |
| `/etc/sudoers`        | Who may use sudo and with which restrictions  |

```bash
cat /etc/passwd            # list users
getent passwd alice        # info about one user
id alice                   # UIDs and GIDs
id                         # yourself
who                        # logged-in users
w                          # more detail: what each user is running
last                       # login history
```

## Creating and managing users

```bash
# Create user with home directory
sudo useradd -m -s /bin/bash alice

# Set password
sudo passwd alice

# One-shot with comment and group
sudo useradd -m -c "Alice Smith" -G docker,developers alice

# Modify existing user
sudo usermod -aG sudo alice          # add to sudo group (append)
sudo usermod -s /bin/zsh alice       # change shell
sudo usermod -L alice                # lock account
sudo usermod -U alice                # unlock

# Delete user (keep home)
sudo userdel alice

# Delete user and home directory
sudo userdel -r alice
```

## Creating and managing groups

```bash
sudo groupadd developers
sudo groupadd -g 1050 infra          # specify GID

sudo gpasswd -a alice developers     # add member
sudo gpasswd -d alice developers     # remove member

sudo groupdel developers
```

After adding yourself to a new group, either log out and back in, or run `newgrp developers` to activate it in the current shell.

## sudo — running commands as root

`sudo` lets privileged users execute commands as root (or another user) without sharing the root password.

```bash
sudo apt update              # run as root
sudo -u postgres psql        # run as the postgres user
sudo !!                      # repeat last command as root
sudo -l                      # what am I allowed to run?
sudo -i                      # interactive root shell
sudo -s                      # root shell preserving environment
```

The configuration lives in `/etc/sudoers`. **Always edit it with `visudo`** — it validates syntax before saving, preventing a locked-out scenario.

```
# /etc/sudoers excerpt
%sudo   ALL=(ALL:ALL) ALL        # sudo group: run anything
alice   ALL=(ALL) NOPASSWD: /usr/bin/systemctl   # passwordless systemctl only
```

## su — switch user

```bash
su - alice          # switch to alice (with her environment)
su -                # switch to root (requires root password)
su alice -c "ls ~"  # run one command as alice
```

In modern setups, prefer `sudo -u alice` over `su alice` — sudo logs every command, `su` does not.

## Minimum-privilege principle

- Each service should run as its own non-root user. For example, nginx runs as `www-data`, postgres as `postgres`.
- Application users should not have a login shell (`/usr/sbin/nologin` or `/bin/false`).
- Give sudo only for specific commands, not blanket `ALL`.

```bash
# Create a system (no-login) account for a service
sudo useradd --system --no-create-home --shell /usr/sbin/nologin myservice
```

This reduces the damage radius if that service is compromised.
