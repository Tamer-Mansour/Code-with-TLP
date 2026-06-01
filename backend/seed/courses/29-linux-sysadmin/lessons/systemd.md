# systemd and Services

`systemd` is the init system and service manager on most modern Linux distros (Ubuntu 16+, Debian 8+, Fedora, CentOS/RHEL 7+, Arch). It replaces SysV init scripts.

## Managing services

```bash
sudo systemctl status nginx
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl reload nginx          # if supported - re-read config

sudo systemctl enable nginx          # start on boot
sudo systemctl disable nginx

sudo systemctl is-enabled nginx
sudo systemctl is-active nginx

systemctl list-units --type=service
systemctl list-units --failed         # what's broken
```

## Writing a unit file

`/etc/systemd/system/my-app.service`:

```ini
[Unit]
Description=My App
After=network.target

[Service]
Type=simple
User=app
WorkingDirectory=/opt/my-app
ExecStart=/opt/my-app/bin/server
Restart=on-failure
RestartSec=5
Environment=NODE_ENV=production
EnvironmentFile=/etc/my-app/env

# resource limits
LimitNOFILE=65535
MemoryMax=512M

# sandboxing
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/log/my-app

[Install]
WantedBy=multi-user.target
```

Reload after editing:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now my-app
```

## Common service types

- **simple** (default) — runs `ExecStart` in foreground.
- **forking** — process daemonizes itself (older daemons).
- **oneshot** — runs once, used for setup tasks.
- **notify** — service signals readiness via `sd_notify` (PostgreSQL, nginx).

## Sandboxing options

Production-grade hardening is just a few config lines:

| Directive                | Effect                                  |
|--------------------------|-----------------------------------------|
| `NoNewPrivileges=true`   | Block setuid escalation                 |
| `PrivateTmp=true`        | Private /tmp per service                |
| `ProtectSystem=strict`   | Read-only / except whitelisted paths    |
| `ProtectHome=true`       | Hide /home from the service             |
| `ReadWritePaths=...`     | Explicit writable paths                 |
| `CapabilityBoundingSet=` | Restrict Linux capabilities             |

`systemctl status my-app` shows a security score; `systemd-analyze security my-app` gives a detailed audit.

## Logs

systemd captures stdout/stderr into the **journal**:

```bash
journalctl -u my-app
journalctl -u my-app -f                 # follow
journalctl -u my-app --since "1 hour ago"
journalctl -u my-app -p err              # priority filter (emerg..debug)
journalctl -k                            # kernel logs (dmesg-style)
```

Persistent storage: `/var/log/journal/` (enabled when the dir exists).

## Timers — cron alternative

```ini
# /etc/systemd/system/backup.service
[Service]
Type=oneshot
ExecStart=/usr/local/bin/backup
```

```ini
# /etc/systemd/system/backup.timer
[Unit]
Description=Daily backup

[Timer]
OnCalendar=daily
Persistent=true             # run on next boot if missed

[Install]
WantedBy=timers.target
```

Enable:

```bash
sudo systemctl enable --now backup.timer
systemctl list-timers
```

Advantages over cron: native integration with systemd logs, dependencies, sandboxing, persistent catch-up.

## User units

Run services as your user, no root needed:

```bash
mkdir -p ~/.config/systemd/user
# put unit file there
systemctl --user enable --now my-app.service
loginctl enable-linger $USER             # run even when not logged in
```

Great for personal background tasks.

## Cheatsheet

- View dependencies: `systemctl list-dependencies my-app`.
- Edit a unit safely (creates override): `sudo systemctl edit my-app`.
- Reset failed state: `sudo systemctl reset-failed my-app`.
- Boot performance: `systemd-analyze blame`.
