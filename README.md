# Smart Farm Pro

Smart Farm Pro is an IoT smart farming platform project. This repository tracks application source code and project documentation.

## Repository Structure

```text
SMART-FARM-PRO/
├── backend/
│   ├── public/api/health.php
│   └── src/Database.php
├── frontend/public/
│   ├── index.php
│   └── health.php
├── .gitignore
└── README.md
```

## Current Components

- `backend/src/Database.php`: PostgreSQL connection handling using external environment configuration.
- `backend/public/api/health.php`: API health endpoint.
- `frontend/public/index.php`: Web service status endpoint returning JSON.
- `frontend/public/health.php`: Web health endpoint returning JSON.

These endpoints provide basic service status information. They do not represent a complete user interface or a fully integrated monitoring system.

## Requirements

- Linux environment
- PHP 8.4 or a compatible version
- PHP PDO PostgreSQL driver (`pdo_pgsql`)
- PostgreSQL
- Apache or another compatible PHP-capable web server for web deployment

Actual requirements may vary as the project develops.

## Database Configuration

The database connection component reads configuration from `/etc/smartfarm/postgres.env`.

Required configuration keys:

- `DB_HOST`
- `DB_PORT`
- `DB_DATABASE`
- `DB_USERNAME`
- `DB_PASSWORD`

Keep this configuration file outside the repository. Set credentials securely in the deployment environment. Never commit database passwords, tokens, private keys, or production secrets.

## Security Guidelines

- Keep production credentials outside the repository.
- Review all changes before staging and committing.
- Do not commit secret-bearing environment files, database dumps, logs, or private keys.
- Preserve existing backups before database or deployment changes.
- Test changes before deploying them to the live service.

## Git Workflow

Check the working tree:

```bash
git status --short --branch
```

Review unstaged changes:

```bash
git diff
```

Stage only intended files, then inspect the staged diff before committing:

```bash
git add README.md
git diff --cached -- README.md
git commit -m "docs: add project README"
git push
```

## Project Status

This repository is being populated incrementally from the existing Smart Farm Pro deployment. Verify implementation details, configuration, and deployment behavior against the current environment before making operational changes.
