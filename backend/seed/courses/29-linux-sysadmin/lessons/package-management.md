# Package Management on Linux

Linux distributions use **package managers** to install, update, and remove software in a consistent and reproducible way. Every installed package is tracked with its version, files, and dependencies.

## Debian/Ubuntu — apt

`apt` (and its lower-level sibling `dpkg`) is used on Debian, Ubuntu, Linux Mint, and most cloud server images.

```bash
# Update the local package index (do this first!)
sudo apt update

# Install a package
sudo apt install nginx

# Remove (keep config files)
sudo apt remove nginx

# Remove + delete config files
sudo apt purge nginx

# Upgrade all installed packages
sudo apt upgrade

# Upgrade + allow package removal if needed
sudo apt full-upgrade

# Search for packages
apt search python3-flask

# Show package info
apt show nginx

# List installed packages
dpkg -l

# Find which package installed a specific file
dpkg -S /usr/bin/python3
```

## Red Hat / CentOS / Fedora — dnf / yum

`dnf` is the modern successor to `yum` on RHEL 8+, Fedora, and Rocky/Alma Linux.

```bash
sudo dnf install httpd          # install
sudo dnf remove httpd           # remove
sudo dnf upgrade                # upgrade all
sudo dnf search httpd           # search
sudo dnf info httpd             # details
sudo dnf list installed         # installed packages
sudo dnf provides /usr/bin/curl # which package owns this file
```

## Repositories

Packages come from **repositories** — curated servers of `.deb` or `.rpm` files.

| Distro    | Repo config path                    |
|-----------|-------------------------------------|
| Debian/Ubuntu | `/etc/apt/sources.list` and `/etc/apt/sources.list.d/` |
| RHEL/Fedora   | `/etc/yum.repos.d/*.repo`      |

Adding a third-party repo (Ubuntu example):

```bash
# Add the key
curl -fsSL https://example.com/gpg.key | sudo gpg --dearmor -o /usr/share/keyrings/example.gpg

# Add the repo
echo "deb [signed-by=/usr/share/keyrings/example.gpg] https://example.com/apt stable main" \
  | sudo tee /etc/apt/sources.list.d/example.list

sudo apt update
sudo apt install example-app
```

## Holding a package version

Sometimes you want to pin a package at a known-good version:

```bash
# apt — hold
sudo apt-mark hold nginx
sudo apt-mark unhold nginx

# dnf — exclude from upgrades in config
# /etc/dnf/dnf.conf: excludepkgs=nginx
```

## Snap and Flatpak

For applications that ship their own dependencies:

```bash
# Snap (Ubuntu canonical)
sudo snap install code --classic

# Flatpak (cross-distro)
flatpak install flathub org.libreoffice.LibreOffice
```

## Best practices

- Always run `apt update` before `apt install` on a fresh system or VM.
- Prefer distribution packages over `pip install` / `npm install -g` for system-wide tools; they benefit from security updates.
- Pin critical packages (like a database engine) in production so unattended upgrades don't break you.
- Use `apt-get` instead of `apt` in scripts — it has a stable CLI, unlike `apt` which may warn about its interface changing.
