# Quiz: Networking and Users

**Q1. Which command shows all TCP listening ports with their owning process?**
- [ ] `netstat -a`
- [x] `ss -tlnp`
- [ ] `ip addr show`
- [ ] `lsof -a`

**Q2. After adding your user to a new group, what must you do for it to take effect in the current shell?**
- [ ] Run `sudo groupadd`
- [ ] Reboot the machine
- [x] Log out and log back in (or run `newgrp <group>`)
- [ ] Run `sudo passwd`

**Q3. What file controls who can use `sudo` and with which restrictions?**
- [ ] `/etc/passwd`
- [ ] `/etc/shadow`
- [x] `/etc/sudoers`
- [ ] `/etc/group`

**Q4. Which `ssh-keygen` key type is the modern recommended default?**
- [ ] `rsa` 2048-bit
- [ ] `dsa`
- [x] `ed25519`
- [ ] `ecdsa` 256-bit

**Q5. You run `journalctl -u nginx -p err`. What does this show?**
- [x] Error-priority and above messages from the nginx unit
- [ ] All nginx logs since the last boot
- [ ] Kernel errors related to networking
- [ ] Nginx config file errors only

**Q6. In a crontab, what does `*/15 * * * *` mean?**
- [ ] Every 15 seconds
- [ ] At minute 15 of every hour
- [x] Every 15 minutes
- [ ] 15 times per day

**Q7. Which command displays disk usage in a human-readable tree view for a directory?**
- [ ] `df -h /var`
- [ ] `lsblk /var`
- [ ] `fdisk -l`
- [x] `du -sh /var/*`

**Q8. What does `sudo usermod -aG docker alice` do?**
- [ ] Creates a new user called docker
- [ ] Removes alice from all groups
- [x] Adds alice to the docker group without removing her from current groups
- [ ] Sets docker as alice's primary group
