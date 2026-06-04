pyproject configuration, based on the generic configuration.

# Overview

## Update to Latest Migration

```bash
alembic upgrade head
```

## Generate new migration
```bash
alembic revision -m "create init migration with media-related tables"
```

## Generate Migrations from code

```bash
alembic revision --autogenerate -m "Generate for Media Tables"
```

## Run Migrations

### Downgrade

- You can downgrade by the full name of by the first four characters of the hash.

```bash
alembic downgrade e241
```

### Upgrade
- You can upgrade by the full name of by the first four characters of the hash.

```bash
alembic upgrade e241
```
