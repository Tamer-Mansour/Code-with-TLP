# Disk and Storage Management

Understanding disk layout, filesystems, and mount points is fundamental to Linux administration. This lesson covers the tools you'll use to inspect and manage storage.

## Viewing disk usage

```bash
df -h                   # disk free — mounted filesystems, human-readable
df -h /var              # just that filesystem
du -sh /var/log         # disk used by a directory
du -sh /*               # top-level sizes
du -sh * | sort -hr     # sorted largest-first
ncdu /var               # interactive ncurses disk usage (install separately)
```

## Block devices

```bash
lsblk                   # tree of block devices and partitions
lsblk -f                # also shows filesystem type and UUID
fdisk -l                # partition table (requires root)
blkid                   # UUIDs and filesystem types
```

Example `lsblk` output:

```
NAME   MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
sda      8:0    0   50G  0 disk
├─sda1   8:1    0  512M  0 part /boot
├─sda2   8:2    0    2G  0 part [SWAP]
└─sda3   8:3    0 47.5G  0 part /
sdb      8:16   0  200G  0 disk
```

## Filesystems

Common Linux filesystem types:

| Filesystem | Notes                                              |
|------------|----------------------------------------------------|
| `ext4`     | Default on most Debian/Ubuntu installations         |
| `xfs`      | Default on RHEL/CentOS; excellent for large files  |
| `btrfs`    | Copy-on-write, snapshots, built-in RAID             |
| `tmpfs`    | In-memory; `/tmp` and `/run` often use it          |
| `vfat`     | FAT32; USB drives, EFI partition                   |

Creating and formatting:

```bash
sudo mkfs.ext4 /dev/sdb1          # format as ext4
sudo mkfs.xfs  /dev/sdb1          # format as xfs
```

## Mounting and unmounting

```bash
sudo mount /dev/sdb1 /mnt/data     # mount manually
sudo umount /mnt/data              # unmount

mount                              # list all currently mounted filesystems
findmnt                            # tree view
```

### Persistent mounts — /etc/fstab

To mount automatically on boot, add a line to `/etc/fstab`:

```
# <device/UUID>                         <mountpoint>  <type>  <options>     <dump> <pass>
UUID=1a2b3c4d-...                        /mnt/data     ext4    defaults,nofail  0      2
tmpfs                                    /tmp          tmpfs   size=1G          0      0
```

Use UUIDs, not device names (`/dev/sdb1`), because device names can change after a reboot. Get the UUID with `blkid`.

After editing fstab, test before rebooting:

```bash
sudo mount -a        # mount all fstab entries; errors appear immediately
```

## Swap

```bash
swapon --show                      # current swap
free -h                            # memory + swap usage

# Create a swap file
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Add to /etc/fstab for persistence
echo '/swapfile  none  swap  sw  0  0' | sudo tee -a /etc/fstab
```

## LVM — Logical Volume Manager

LVM adds a flexible abstraction layer above physical disks:

```
Physical Volumes (PVs) → Volume Group (VG) → Logical Volumes (LVs)
```

```bash
pvs                        # physical volumes
vgs                        # volume groups
lvs                        # logical volumes

# Extend a logical volume and the filesystem on it
sudo lvextend -L +10G /dev/vg0/data
sudo resize2fs /dev/vg0/data      # ext4
sudo xfs_growfs /mnt/data         # xfs
```

## Quick disk health check

```bash
sudo smartctl -a /dev/sda         # S.M.A.R.T. data (install smartmontools)
dmesg | grep -i "error\|fail"     # kernel disk error messages
iostat -xz 1                      # real-time I/O stats (sysstat package)
```

A machine running out of disk space is one of the most common production incidents. Set up monitoring with `df` in a cron job and alert before `/` reaches 85%.
