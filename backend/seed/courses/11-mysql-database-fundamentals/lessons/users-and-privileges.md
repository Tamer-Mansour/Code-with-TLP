# Users, Roles, and GRANT

MySQL's permission model is fine-grained: **users** are granted specific privileges on specific objects. Get this right and a bug in your app can't `DROP TABLE` your prod data.

## Creating a user

```sql
CREATE USER 'app'@'%' IDENTIFIED BY 'a-strong-password';
```

The `'name'@'host'` form is a *pair* — `'app'@'10.0.%'` and `'app'@'%'` are two different users with potentially different passwords.

## Granting privileges

```sql
GRANT SELECT, INSERT, UPDATE, DELETE ON shop.* TO 'app'@'%';
FLUSH PRIVILEGES;
```

Common privileges:

| Privilege          | Lets you...                                   |
|--------------------|-----------------------------------------------|
| `SELECT`           | read rows                                     |
| `INSERT`           | add rows                                      |
| `UPDATE`           | modify rows                                   |
| `DELETE`           | remove rows                                   |
| `CREATE`, `DROP`   | create/drop tables                            |
| `ALTER`            | change table schema                           |
| `INDEX`            | create indexes                                |
| `EXECUTE`          | run stored procedures                         |
| `ALL PRIVILEGES`   | everything (avoid for app users)              |

## Principle of least privilege

Your application user should have **just enough** to do its job. A read-only reporting tool gets `SELECT` only. A migration job gets DDL temporarily. The application itself almost never needs `DROP`.

```sql
CREATE USER 'readonly'@'%' IDENTIFIED BY '...';
GRANT SELECT ON shop.* TO 'readonly'@'%';
```

## Roles (MySQL 8)

Roles let you bundle privileges:

```sql
CREATE ROLE 'app_read', 'app_write';
GRANT SELECT ON shop.* TO 'app_read';
GRANT INSERT, UPDATE, DELETE ON shop.* TO 'app_write';

CREATE USER 'app'@'%' IDENTIFIED BY '...';
GRANT 'app_read', 'app_write' TO 'app'@'%';
SET DEFAULT ROLE ALL TO 'app'@'%';
```

## Inspecting

```sql
SHOW GRANTS FOR 'app'@'%';
SELECT user, host FROM mysql.user;
```

## Revoking and dropping

```sql
REVOKE INSERT ON shop.* FROM 'app'@'%';
DROP USER 'app'@'%';
```

## Password policy

MySQL 8 includes a password validation plugin (`validate_password`). Tune `validate_password.policy = STRONG` to require length + mixed case + symbols.

## Connection encryption

For production, require TLS:

```sql
ALTER USER 'app'@'%' REQUIRE SSL;
```

Connect with `--ssl-mode=REQUIRED` from clients. Most managed services enforce this by default.

## Don't use root from your application

`root@localhost` exists for administration. Create a per-service user, grant it the minimum, and rotate its password.
