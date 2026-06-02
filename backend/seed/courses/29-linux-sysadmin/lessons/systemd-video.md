# Video: systemd Crash Course

This video walks through systemd — the init system and service manager used in virtually all modern Linux distributions. It covers service units, the journal, timers, and targets with practical live demonstrations.

Key takeaways covered in the video:

- Understanding unit files (`.service`, `.timer`, `.target`, `.socket`) and their sections
- Starting, stopping, enabling, and disabling services with `systemctl`
- Reading and filtering logs with `journalctl` including time ranges and priority filters
- Writing a simple custom service unit from scratch and troubleshooting with `systemctl status`
- How systemd targets replace the traditional SysV runlevels

This is an excellent companion to the written systemd and log management lessons in this course.
