# Installation: MySQL and a Client

MySQL 8 is the relational database engine used throughout this course. This lesson gets the server running on your machine, adds a GUI client so you can explore data visually, and verifies the connection you will rely on in every persistence lab.

---

## Why MySQL 8?

MySQL 8.0 introduced features that matter for modern Spring Boot development: window functions, CTEs (`WITH` clauses), roles, invisible indexes, and significantly improved JSON support. Sticking to 8.x ensures that every SQL statement in this course runs without modification on any supported platform.

---

## Step 1 — Install the MySQL Server

### Windows

The MySQL Installer bundles the server, shell, and optional tools in a single wizard.

```bash
# Option A: winget (Windows 10/11)
winget install Oracle.MySQL

# Option B: download the full installer from
# https://dev.mysql.com/downloads/installer/
# Choose "mysql-installer-community-8.x.x.msi"
# Select: MySQL Server + MySQL Workbench + MySQL Shell
```

During setup, choose **Developer Default** and set a strong root password. Write it down — recovery without it requires stopping the server in safe mode.

### macOS

```bash
# Homebrew (recommended)
brew install mysql@8.4

# Start the service
brew services start mysql@8.4

# Secure the install (sets root password, removes test DB)
mysql_secure_installation
```

If Homebrew installs a different slot (e.g., `mysql` instead of `mysql@8.4`), check the version with `mysql --version` and use whatever alias it creates.

### Linux (Debian / Ubuntu)

```bash
# Add the official APT repository
wget https://dev.mysql.com/get/mysql-apt-config_0.8.30-1_all.deb
sudo dpkg -i mysql-apt-config_0.8.30-1_all.deb
# In the dialog, confirm MySQL 8.x is selected, then OK

sudo apt-get update
sudo apt-get install -y mysql-server

# Enable and start the daemon
sudo systemctl enable --now mysql

# Secure the installation
sudo mysql_secure_installation
```

---

## Step 2 — Verify the Server

After installation, confirm the server is up and the version is correct:

```bash
mysql -u root -p
```

```sql
-- Inside the MySQL shell
SELECT VERSION();
-- Expected output: 8.x.x

SHOW DATABASES;
-- Expected: information_schema, mysql, performance_schema, sys

EXIT;
```

If the `mysql` command is not found on Windows, add the MySQL `bin` directory (e.g., `C:\Program Files\MySQL\MySQL Server 8.0\bin`) to your `PATH` environment variable.

---

## Step 3 — Create an Application User

Never use `root` from your Spring Boot application. Create a dedicated user with a limited scope:

```sql
-- Log in as root first
CREATE USER 'tlp_user'@'localhost' IDENTIFIED BY 'StrongPass1!';

-- Grant full access to any database whose name starts with "tlp_"
GRANT ALL PRIVILEGES ON `tlp_%`.* TO 'tlp_user'@'localhost';

FLUSH PRIVILEGES;

-- Verify
SHOW GRANTS FOR 'tlp_user'@'localhost';
```

Use this user in every `application.properties` file throughout the course:

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/tlp_demo?useSSL=false&serverTimezone=UTC
spring.datasource.username=tlp_user
spring.datasource.password=StrongPass1!
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver
```

---

## Step 4 — Install a GUI Client

A GUI client is not strictly required, but it dramatically speeds up schema exploration and query iteration. The two best free options for this stack are:

| Client | Platform | Strengths |
|---|---|---|
| **MySQL Workbench** | Windows, macOS, Linux | Official, includes EER diagram editor, built-in with MySQL Installer |
| **DBeaver Community** | Windows, macOS, Linux | Multi-database, IntelliJ-style shortcuts, free |
| **IntelliJ Database Tools** | Windows, macOS, Linux | Built into IntelliJ IDEA Ultimate; also available as DataGrip |

For this course, **MySQL Workbench** or **DBeaver Community** are recommended. Both are free and sufficient for everything covered here.

### Connecting in DBeaver

1. Open DBeaver and click **New Database Connection** (the plug icon).
2. Select **MySQL** and click **Next**.
3. Fill in the fields:

```
Host:     localhost
Port:     3306
Database: (leave blank to see all)
Username: tlp_user
Password: StrongPass1!
```

4. Click **Test Connection**. DBeaver may prompt you to download the JDBC driver — allow it.
5. Click **Finish**.

You should now see the server node in the left panel. Expand it to browse schemas, tables, and data.

---

## Step 5 — Create a Test Database

Confirm the application user can create a schema:

```sql
-- Run as tlp_user (in Workbench, DBeaver, or the MySQL shell)
CREATE DATABASE tlp_demo
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE tlp_demo;

CREATE TABLE test_connection (
    id   INT AUTO_INCREMENT PRIMARY KEY,
    msg  VARCHAR(255) NOT NULL
);

INSERT INTO test_connection (msg) VALUES ('MySQL is working!');

SELECT * FROM test_connection;
```

Expected output:

```
+----+-------------------+
| id | msg               |
+----+-------------------+
|  1 | MySQL is working! |
+----+-------------------+
```

Clean up when done:

```sql
DROP DATABASE tlp_demo;
```

---

## Common Mistakes

- **Connecting as root from application code.** If your credentials are ever exposed, an attacker gets full server access. Always use a least-privilege application user.
- **Forgetting `?serverTimezone=UTC` in the JDBC URL.** Without it, the MySQL JDBC driver throws a `MismatchedTimeZoneException` on many systems.
- **Character set mismatch.** Always create databases with `utf8mb4` (not the legacy `utf8`), which is the only encoding that correctly stores all Unicode characters including emoji.
- **Firewall blocking port 3306.** On Linux, if a remote client cannot connect, check `sudo ufw status` and open the port if needed — though for local development `localhost` connections bypass the firewall.
- **Multiple MySQL versions on macOS.** If you previously installed MySQL via a `.dmg` package, Homebrew installs may conflict. Run `which mysql` and `mysql --version` to confirm which binary is active.

---

## Summary

Install MySQL 8 using the platform-appropriate method, secure the root account, create a dedicated `tlp_user` application account, and verify the connection through both the CLI and a GUI client. Every Spring Boot persistence lab in this course connects through `tlp_user` on `localhost:3306`.
