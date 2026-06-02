# Networking Basics for Linux Admins

Linux ships with a powerful set of networking tools. This lesson covers the essential commands for inspecting interfaces, connectivity, DNS, and open ports.

## Network interfaces

```bash
ip link show            # list all interfaces
ip addr show            # interfaces + IP addresses
ip addr show eth0       # specific interface
ip route show           # routing table
ip route get 8.8.8.8    # which route will be used for this destination
```

The legacy `ifconfig` and `route` (from net-tools) are deprecated on modern distros. Prefer `ip`.

## Connectivity checks

```bash
ping -c 4 google.com          # 4 ICMP echo packets
ping6 ::1                     # IPv6 loopback
traceroute google.com         # hop-by-hop path
mtr google.com                # live traceroute (ncurses)
```

## DNS

```bash
dig google.com                # full DNS query output
dig google.com MX             # mail records
dig @8.8.8.8 google.com       # query specific resolver
host google.com               # simple lookup
nslookup google.com           # legacy (still widely installed)
resolvectl status             # systemd-resolved current config
cat /etc/resolv.conf          # resolver configuration
```

## Open ports and sockets

```bash
ss -tlnp            # TCP listening sockets with process names
ss -ulnp            # UDP listening
ss -anp             # all sockets
netstat -tlnp       # legacy equivalent (net-tools)
lsof -i :80         # which process is on port 80
lsof -i tcp:443     # HTTPS
```

| ss flag | Meaning                    |
|---------|----------------------------|
| `-t`    | TCP                        |
| `-u`    | UDP                        |
| `-l`    | Listening only             |
| `-n`    | Show numbers, not names    |
| `-p`    | Show owning process        |

## Firewall — ufw and iptables

**ufw** (Uncomplicated Firewall) is the standard on Ubuntu:

```bash
sudo ufw status               # current rules
sudo ufw enable
sudo ufw allow 22             # SSH
sudo ufw allow 80/tcp
sudo ufw allow from 10.0.0.0/8 to any port 5432  # restrict by source
sudo ufw delete allow 80/tcp
```

Under the hood, ufw writes `iptables` rules. For low-level inspection:

```bash
sudo iptables -L -n -v        # all chains
sudo iptables -S              # rules as commands
```

## Temporary network configuration

Changes made with `ip` are not persistent across reboots. For persistence, configure your distro's network manager:

- **Ubuntu server**: edit `/etc/netplan/*.yaml`, then `sudo netplan apply`
- **RHEL/CentOS**: `nmcli` or edit `/etc/sysconfig/network-scripts/ifcfg-<dev>`

```bash
# Temporary: bring up an interface with a static IP
sudo ip addr add 192.168.1.100/24 dev eth0
sudo ip link set eth0 up
sudo ip route add default via 192.168.1.1
```

## Useful one-liners

```bash
# Download a file
curl -O https://example.com/file.tar.gz
wget https://example.com/file.tar.gz

# Check HTTP response code
curl -o /dev/null -sw "%{http_code}\n" http://localhost:8080/health

# Scan a port (requires nc/ncat)
nc -zv 10.0.0.5 5432
```

Understanding these basics lets you diagnose connection failures, confirm which service is on which port, and harden a server before exposing it to the internet.
