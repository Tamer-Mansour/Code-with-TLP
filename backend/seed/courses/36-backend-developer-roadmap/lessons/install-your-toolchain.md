# Installation: JDK, IDE, Git, MySQL, Node, and Browser Tools

Every backend project in this course depends on the same set of tools. Install them once in the right order and every lab will just work. This lesson walks you through each piece of the stack, gives you the exact commands to verify a successful install, and flags the mistakes most beginners make.

---

## Tool Overview

| Tool | Purpose in this course | Minimum version |
|---|---|---|
| JDK (Temurin 21) | Compile and run Java / Spring Boot | 21 LTS |
| IntelliJ IDEA | IDE with Spring Boot support | 2024.x Community |
| Git | Version control, clone lab repos | 2.40+ |
| MySQL 8 | Relational database for all persistence labs | 8.0+ |
| Node.js / npm | Run front-end tooling, Vite, and seed scripts | 20 LTS |
| Chrome + DevTools | Test REST responses, inspect headers | latest stable |

---

## 1. JDK 21 (Eclipse Temurin)

Use Temurin — it is free, production-grade, and has long-term support.

**Windows**
```bash
# Using winget (Windows 10/11)
winget install EclipseAdoptium.Temurin.21.JDK

# Verify
java -version
# Expected: openjdk version "21.x.x" ...
javac -version
# Expected: javac 21.x.x
```

**macOS**
```bash
brew install --cask temurin@21
java -version
```

**Linux (Debian/Ubuntu)**
```bash
sudo apt-get install -y wget apt-transport-https
wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public | sudo apt-key add -
echo "deb https://packages.adoptium.net/artifactory/deb $(lsb_release -sc) main" \
  | sudo tee /etc/apt/sources.list.d/adoptium.list
sudo apt-get update && sudo apt-get install -y temurin-21-jdk
java -version
```

Set `JAVA_HOME` so build tools can find the JDK:
```bash
# macOS / Linux — add to ~/.bashrc or ~/.zshrc
export JAVA_HOME=$(dirname $(dirname $(readlink -f $(which java))))
export PATH=$JAVA_HOME/bin:$PATH
```

---

## 2. IntelliJ IDEA (Community Edition)

Download the Community Edition from [jetbrains.com/idea](https://www.jetbrains.com/idea/download/). During setup:

- Accept the default installation directory.
- Enable **"Add launchers dir to PATH"** on Windows.
- Install the **Spring Boot** and **Database Tools** plugins from `Settings → Plugins` after first launch.

Verify the IDE sees your JDK via `File → Project Structure → SDKs`.

---

## 3. Git

**Windows**
```bash
winget install Git.Git
git --version   # git version 2.x.x
```

**macOS**
```bash
brew install git
git --version
```

**Linux**
```bash
sudo apt-get install -y git
git --version
```

Configure your identity immediately — Git embeds this in every commit:
```bash
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"
git config --global core.autocrlf input   # keeps line endings consistent
```

---

## 4. MySQL 8

**Windows / macOS** — use the [MySQL Installer](https://dev.mysql.com/downloads/installer/) and select **Server + MySQL Workbench**.

**Linux**
```bash
sudo apt-get install -y mysql-server
sudo systemctl enable --now mysql
sudo mysql_secure_installation   # set root password, remove test DB
```

Verify the server is running and log in:
```bash
mysql -u root -p
```
```sql
-- Inside the MySQL shell
SELECT VERSION();
-- Expected: 8.x.x
EXIT;
```

Create a dedicated user for labs (never connect as root from application code):
```sql
CREATE USER 'tlp_user'@'localhost' IDENTIFIED BY 'StrongPass1!';
GRANT ALL PRIVILEGES ON *.* TO 'tlp_user'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

---

## 5. Node.js 20 LTS

Node is needed for front-end build steps and several seed/utility scripts in the course.

**All platforms (recommended — use nvm)**
```bash
# Install nvm first: https://github.com/nvm-sh/nvm
nvm install 20
nvm use 20
node -v   # v20.x.x
npm  -v   # 10.x.x
```

**Windows (winget)**
```bash
winget install OpenJS.NodeJS.LTS
node -v
npm  -v
```

---

## 6. Chrome Developer Tools

No install needed — Chrome ships with DevTools. Open them with `F12` or `Ctrl+Shift+I` (`Cmd+Option+I` on Mac).

Key tabs you will use throughout this course:

- **Network** — inspect HTTP requests, response headers, and status codes from your Spring Boot API.
- **Console** — run ad-hoc JavaScript when testing front-end integrations.
- **Application → Storage** — view cookies, `localStorage`, and session data.

---

## Common Mistakes

- **Wrong JAVA_HOME** — If `mvn` or Gradle picks up a system JRE instead of JDK 21, your builds will fail with `source release 21 requires target release 21`. Fix: confirm `echo $JAVA_HOME` points to the Temurin 21 directory.
- **MySQL root password forgotten** — Always note the root password during `mysql_secure_installation`; recovery requires stopping the server in safe mode.
- **Node version mismatch** — Some npm scripts in this course require Node 18+. Always pin versions with `nvm use 20` at the start of a session.
- **Line ending issues on Windows** — Set `core.autocrlf input` in Git to avoid CRLF/LF conflicts when collaborating across operating systems.

---

## Summary

Install JDK 21, IntelliJ IDEA, Git, MySQL 8, and Node 20 LTS in order, verify each with the commands above, and configure your Git identity and MySQL application user before moving on. Every subsequent lab in this course assumes this toolchain is in place.
