# Quiz: Networking and Security Hardening

**Q1. Which command shows all active TCP connections and the processes that own them?**
- [ ] `ip addr show`
- [ ] `ping -l`
- [x] `ss -tnp`
- [ ] `traceroute -t`

**Q2. You need to determine the IP address a hostname resolves to and which DNS server answered. Which tool is best?**
- [ ] `ping hostname`
- [ ] `nslookup hostname` (classic, limited output)
- [x] `dig hostname` (full DNS response including server and TTL)
- [ ] `curl -I hostname`

**Q3. Which file on Linux defines static hostname-to-IP mappings that are checked BEFORE DNS?**
- [ ] `/etc/resolv.conf`
- [x] `/etc/hosts`
- [ ] `/etc/nsswitch.conf`
- [ ] `/etc/hostname`

**Q4. What is the purpose of the SSH `PermitRootLogin no` directive in `/etc/sshd_config`?**
- [ ] It prevents the root user from being created on the system
- [ ] It disables password authentication entirely
- [x] It prevents direct SSH login as root, forcing admins to login as a normal user and then escalate
- [ ] It removes root from the sudoers file

**Q5. Which firewall tool is the modern default on RHEL/CentOS/Fedora systems?**
- [ ] `iptables` directly
- [ ] `ufw`
- [x] `firewalld` (which wraps nftables/iptables as its backend)
- [ ] `nftables` CLI directly

**Q6. You run `traceroute 8.8.8.8` and one hop shows `* * *`. What does this indicate?**
- [ ] That hop is offline and the route is broken
- [x] That router dropped the TTL-expired ICMP packets (filtered), not necessarily that it's down
- [ ] That 8.8.8.8 is unreachable from your machine
- [ ] That your local machine has no route to 8.8.8.8

**Q7. What is the correct way to generate a modern SSH key pair for authentication?**
- [ ] `ssh-keygen -t rsa -b 1024`
- [ ] `ssh-keygen -t dsa`
- [x] `ssh-keygen -t ed25519`
- [ ] `openssl genrsa -out id_rsa 2048`

**Q8. Which command adds a permanent firewall rule to allow port 443/tcp using firewalld?**
- [ ] `iptables -A INPUT -p tcp --dport 443 -j ACCEPT`
- [ ] `ufw allow 443/tcp`
- [x] `firewall-cmd --permanent --add-port=443/tcp && firewall-cmd --reload`
- [ ] `nft add rule inet filter input tcp dport 443 accept`
