# Cron and Task Scheduling

Linux provides several mechanisms for running commands on a schedule. **cron** is the classic daemon; **systemd timers** are the modern alternative that integrates with the service manager.

## The cron daemon

`cron` reads job definitions called **crontabs** and executes them at the specified times. Every user can have their own crontab; the root crontab and `/etc/cron.d/` files define system-wide jobs.

```bash
crontab -e          # edit your crontab (opens $EDITOR)
crontab -l          # list your crontab
crontab -r          # remove your crontab (careful!)
crontab -u alice -l # list another user's crontab (root only)
```

## Crontab syntax

```
┌──────── minute        (0–59)
│ ┌────── hour          (0–23)
│ │ ┌──── day of month  (1–31)
│ │ │ ┌── month         (1–12)
│ │ │ │ ┌ day of week   (0–7, 0 and 7 = Sunday)
│ │ │ │ │
* * * * *   command to run
```

### Examples

```cron
# Every minute
* * * * *  /usr/local/bin/check_health.sh

# Every day at 2:30 AM
30 2 * * *  /usr/local/bin/backup.sh

# Every Monday at midnight
0 0 * * 1  /usr/local/bin/weekly_report.sh

# Every 15 minutes
*/15 * * * *  /usr/local/bin/sync.sh

# First day of each month at 6 AM
0 6 1 * *  /usr/local/bin/monthly_cleanup.sh

# At 8 AM, Mon–Fri
0 8 * * 1-5  /usr/local/bin/send_summary.sh
```

Special strings (not all cron implementations support these):

| String      | Equivalent     |
|-------------|----------------|
| `@reboot`   | Once, at boot  |
| `@hourly`   | `0 * * * *`    |
| `@daily`    | `0 0 * * *`    |
| `@weekly`   | `0 0 * * 0`    |
| `@monthly`  | `0 0 1 * *`    |

Use [crontab.guru](https://crontab.guru) to verify expressions interactively.

## System-wide cron locations

| Path                    | Who edits it         |
|-------------------------|----------------------|
| `/etc/crontab`          | Root, has a USER column |
| `/etc/cron.d/`          | Packages drop files here |
| `/etc/cron.hourly/`     | Scripts run hourly   |
| `/etc/cron.daily/`      | Scripts run daily    |
| `/etc/cron.weekly/`     | Scripts run weekly   |
| `/etc/cron.monthly/`    | Scripts run monthly  |

## Capturing output

By default, cron emails output to the local user. To redirect instead:

```cron
0 2 * * * /usr/local/bin/backup.sh >> /var/log/backup.log 2>&1
```

Or silence it:

```cron
0 2 * * * /usr/local/bin/backup.sh > /dev/null 2>&1
```

## systemd timers — the modern approach

Timers are systemd units with a `.timer` suffix, paired with a `.service` unit to run.

```ini
# /etc/systemd/system/my-cleanup.timer
[Unit]
Description=Run my-cleanup every night

[Timer]
OnCalendar=daily
Persistent=true        # run missed job if system was off

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/my-cleanup.service
[Unit]
Description=My Cleanup Job

[Service]
Type=oneshot
ExecStart=/usr/local/bin/cleanup.sh
User=nobody
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now my-cleanup.timer

systemctl list-timers           # all active timers
journalctl -u my-cleanup.service  # logs from last run
```

## Choosing between cron and systemd timers

| Feature                | cron              | systemd timer            |
|------------------------|-------------------|--------------------------|
| Logging                | Email / redirect  | journald (automatic)     |
| Missed-run recovery    | No                | Yes (`Persistent=true`)  |
| Dependency handling    | No                | Yes (After=, Requires=)  |
| Per-user              | Yes               | Possible (user units)    |
| Simple one-liner       | Yes               | Verbose                  |

For simple periodic tasks, cron is fine. For production workloads that need logging, retry, and dependency awareness, prefer systemd timers.
