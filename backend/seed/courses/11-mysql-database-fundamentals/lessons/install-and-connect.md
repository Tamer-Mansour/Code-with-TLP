# Installing MySQL and Connecting

Three common ways to get a MySQL server running locally:

## 1. Docker (recommended for learning)

```bash
docker run --name mysql8 \
  -e MYSQL_ROOT_PASSWORD=secret \
  -p 3306:3306 \
  -d mysql:8.0
```

Stop and remove cleanly when you're done:

```bash
docker stop mysql8 && docker rm mysql8
```

No installer, no system pollution, and you can spin up a clean version any time.

## 2. Native install

- **macOS:** `brew install mysql && brew services start mysql`
- **Ubuntu/Debian:** `sudo apt install mysql-server && sudo systemctl start mysql`
- **Windows:** download the MSI from `dev.mysql.com/downloads/installer`.

## 3. Hosted MySQL

For real applications you'll use a managed service: AWS RDS, Google Cloud SQL, PlanetScale, DigitalOcean Managed DB. You give them a config; they give you a hostname.

## Connecting

The CLI client is `mysql`:

```bash
mysql -h 127.0.0.1 -P 3306 -u root -p
```

It will prompt for the password (don't put it on the command line — it shows up in your shell history).

Once connected you'll see:

```
mysql>
```

That's the SQL prompt. Every command must end with `;` (or `\g`).

## Create your first database

```sql
CREATE DATABASE shop;
USE shop;
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(200) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
SHOW TABLES;
DESCRIBE users;
```

## Useful client commands

| Command          | What it does                          |
|------------------|---------------------------------------|
| `\?` or `help`   | Show built-in help                    |
| `\s` or `status` | Show server version, connection info  |
| `\u shop`        | Switch to database `shop`             |
| `\q`             | Quit                                  |
| `source f.sql`   | Run all statements from a file        |

## Connection URL form

Most clients also accept a URL:

```
mysql://root:secret@127.0.0.1:3306/shop
```

That's the same connection — host, port, user, password, and database — packed into one string. Your application's database driver will use this form.
