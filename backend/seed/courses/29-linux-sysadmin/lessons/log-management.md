# Log Management

Logs are the first thing you check when something goes wrong. Linux produces logs from the kernel, system services, and applications. Knowing where they live and how to query them quickly is a critical sysadmin skill.

## Key log locations

| Path / Source             | Contains                                      |
|---------------------------|-----------------------------------------------|
| `/var/log/syslog`         | General system messages (Debian/Ubuntu)        |
| `/var/log/messages`       | Same, on RHEL/CentOS                           |
| `/var/log/auth.log`       | Authentication, sudo, SSH (Debian/Ubuntu)      |
| `/var/log/secure`         | Same, on RHEL/CentOS                           |
| `/var/log/kern.log`       | Kernel messages                               |
| `/var/log/dpkg.log`       | Package install/remove history (Debian/Ubuntu) |
| `/var/log/apt/history.log`| apt history                                   |
| `/var/log/nginx/`         | nginx access and error logs                   |
| `journald` (in memory/disk)| systemd journal — covers almost everything   |

## Reading logs

```bash
tail -f /var/log/syslog          # follow in real time
tail -100 /var/log/auth.log      # last 100 lines
less +G /var/log/nginx/access.log # open at end; press Shift-F to follow

grep "ERROR" /var/log/app.log
grep -i "fail\|error\|crit" /var/log/syslog | tail -50
```

## journalctl — the systemd journal

On modern distros, most logs land in the systemd journal:

```bash
journalctl                           # all logs, oldest first
journalctl -n 50                     # last 50 lines
journalctl -f                        # follow (like tail -f)
journalctl -u nginx                  # logs for a specific unit
journalctl -u nginx -f               # follow a unit
journalctl --since "1 hour ago"
journalctl --since "2024-01-15 10:00" --until "2024-01-15 11:00"
journalctl -p err                    # only priority: error and above
journalctl -p err -u sshd            # errors from sshd
journalctl -k                        # kernel messages only
journalctl -b                        # current boot
journalctl -b -1                     # previous boot
```

## Log rotation — logrotate

Log files would grow forever without rotation. `logrotate` truncates and archives old logs on a schedule.

```bash
logrotate --debug /etc/logrotate.conf    # dry-run: what would it do?
cat /etc/logrotate.d/nginx               # nginx-specific config
```

Example config:

```
/var/log/myapp/*.log {
    daily
    rotate 14          # keep 14 days
    compress           # gzip old logs
    delaycompress      # keep yesterday uncompressed
    missingok          # don't error if missing
    notifempty         # skip if empty
    postrotate
        systemctl reload myapp
    endscript
}
```

## Searching across logs

```bash
# Find all SSH login failures in auth.log
grep "Failed password" /var/log/auth.log | awk '{print $11}' | sort | uniq -c | sort -rn

# Check kernel OOM killer
dmesg | grep -i "oom\|kill"
journalctl -k | grep -i oom

# Audit failed sudo attempts
grep "FAILED" /var/log/auth.log
```

## Centralized logging

In multi-server environments, logs from every machine are shipped to a central service:

- **rsyslog / syslog-ng** — local daemons that can forward to a remote server or a cloud log aggregator.
- **Loki + Grafana** — lightweight, label-based log aggregation (cloud-native).
- **Elasticsearch + Logstash + Kibana (ELK/EFK)** — powerful search and dashboards.
- **Cloud options** — AWS CloudWatch Logs, GCP Cloud Logging, Azure Monitor.

A simple rsyslog forward rule to a remote server:

```
# /etc/rsyslog.d/50-remote.conf
*.* @@logs.example.com:514    # TCP; @ = UDP
```

Good logging hygiene means logs are structured (JSON), timestamped in UTC, and retained long enough for your compliance requirements (often 30–90 days for application logs, 1 year for audit logs).
