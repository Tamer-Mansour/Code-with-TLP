# Logins, Users, and Roles

SQL Server's auth model has two layers:

- **Logins** live at the **server** level — they let someone connect.
- **Users** live at the **database** level — they let a login do things inside one DB.

A single login can map to users in many databases.

## Creating a login

Windows auth (recommended for domain users):

```sql
CREATE LOGIN [DOMAIN\alice] FROM WINDOWS;
```

SQL auth (username + password):

```sql
CREATE LOGIN app WITH PASSWORD = 'a-strong-password',
                     CHECK_POLICY = ON;
```

`CHECK_POLICY` ties the login's password to the host's password policy (length, complexity, lockout).

## Mapping a user inside a database

```sql
USE shop;
CREATE USER app FOR LOGIN app;
```

Now `app` exists in the `shop` database and can be granted privileges.

## Permissions

```sql
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::dbo TO app;
GRANT EXECUTE ON SCHEMA::dbo TO app;
```

Granting at the **schema** level is usually cleaner than per-object. Common alternatives:

```sql
GRANT SELECT ON dbo.users TO readonly_role;
DENY  SELECT ON dbo.audit_log TO readonly_role;
```

`DENY` overrides `GRANT` even via role membership — handy for one-off restrictions.

## Built-in database roles

| Role                 | What it grants                          |
|----------------------|-----------------------------------------|
| `db_owner`           | Everything in the DB. Use sparingly.    |
| `db_datareader`      | `SELECT` on all tables.                 |
| `db_datawriter`      | `INSERT`/`UPDATE`/`DELETE` on all.      |
| `db_ddladmin`        | Run DDL (CREATE/DROP/ALTER).            |
| `db_securityadmin`   | Manage permissions and roles.           |

Add a user to a role:

```sql
ALTER ROLE db_datareader ADD MEMBER app;
```

## Custom roles

```sql
CREATE ROLE app_reader;
GRANT SELECT ON SCHEMA::dbo TO app_reader;
ALTER ROLE app_reader ADD MEMBER app;
```

Roles are how you keep permissions sane: grant rights to a *role*, add *users* to the role.

## Server-level roles

| Role                | Powers                                |
|---------------------|---------------------------------------|
| `sysadmin`          | God mode. Avoid for app accounts.     |
| `securityadmin`     | Manage logins.                        |
| `dbcreator`         | Create databases.                     |
| `serveradmin`       | Configure server settings.            |

A least-privilege app login is in **no server role**, mapped only to one database, granted only the schemas it needs.

## Orphaned users

If you restore a database to a different server, users may exist without matching logins. Fix with:

```sql
ALTER USER app WITH LOGIN = app;
```

## Contained databases

A newer model where users live entirely inside the database (no separate login) — easier to move databases between servers. Enable per-database with `ALTER DATABASE shop SET CONTAINMENT = PARTIAL;` then `CREATE USER app WITH PASSWORD = '...';`
