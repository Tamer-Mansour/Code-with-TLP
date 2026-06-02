# Setting Up Git — Installation and Configuration

Before you write a single commit, Git needs to know who you are and how you like to work. This lesson covers installation, essential global settings, and a few quality-of-life tweaks that pay off immediately.

## Installing Git

| Platform | Method |
|----------|--------|
| Windows  | Download from [git-scm.com](https://git-scm.com) or `winget install Git.Git` |
| macOS    | `brew install git` (Homebrew) or Xcode Command Line Tools |
| Linux    | `sudo apt install git` / `sudo dnf install git` |

Verify the installation:

```bash
git --version
# git version 2.44.0
```

Always use a modern Git (2.30+). Many quality-of-life features and safer defaults arrived after 2.28.

## First-time identity setup

Git embeds your name and email into every commit you make. This is **not** authentication — it is just metadata.

```bash
git config --global user.name "Alice Cheng"
git config --global user.email "alice@example.com"
```

`--global` writes to `~/.gitconfig`. Inside a specific repo, drop the flag to override on a per-project basis (useful when you use different emails for work vs. personal projects).

## Recommended global settings

```bash
# Default branch name for new repos (matches GitHub/GitLab default)
git config --global init.defaultBranch main

# Rebase instead of merge on git pull (keeps a cleaner linear history)
git config --global pull.rebase true

# Make git push send the current branch by default
git config --global push.autoSetupRemote true

# Set your preferred editor (VS Code, Vim, Nano, etc.)
git config --global core.editor "code --wait"

# Color output always on (even when piped)
git config --global color.ui auto
```

## View your config

```bash
git config --list            # all resolved settings
git config --list --global   # only global settings
git config user.email        # a single value
```

Config is stored in three files that layer on top of each other:

```
~/.gitconfig          (global)    ← lowest priority for duplicates
<repo>/.git/config    (local)     ← overrides global
<system>/etc/gitconfig (system)  ← rarely touched
```

## Useful aliases to set up now

Aliases let you create short commands for common operations:

```bash
git config --global alias.s  "status -sb"
git config --global alias.l  "log --oneline --graph --decorate --all"
git config --global alias.co "checkout"
git config --global alias.aa "add --all"
git config --global alias.unstage "restore --staged"
```

Now `git l` shows a nice branch graph, and `git s` gives a clean status overview.

## Verify everything is in order

```bash
git config --list --show-origin
```

This shows each setting alongside the file it came from, which is invaluable when debugging unexpected behavior.

## SSH key setup (for GitHub / GitLab)

Password-based Git auth over HTTPS was deprecated. Use SSH:

```bash
ssh-keygen -t ed25519 -C "alice@example.com"
# Press Enter to accept defaults
cat ~/.ssh/id_ed25519.pub
# Copy the output and paste into GitHub → Settings → SSH keys
```

Test the connection:

```bash
ssh -T git@github.com
# Hi Alice! You've successfully authenticated, but GitHub does not provide shell access.
```

With SSH configured you can `git clone git@github.com:alice/project.git` without entering a password.
