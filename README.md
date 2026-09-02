# EZPZ Client Database — Flask CRUD

A structured client-profile application with create, read, update, delete, Active/Inactive filtering, and unlimited key contacts and EZPZ team members.

## Folder structure

```
.
├── app.py                 # Entry point; creates the Flask app (python app.py)
├── create_tables.py       # Standalone: creates the MySQL tables (peewee)
├── seeder.py              # Standalone: copies instance/clients.db (SQLite) → MySQL
├── models.py              # Standalone peewee models shared by create_tables.py / seeder.py
├── res/
│   ├── __init__.py
│   ├── main.py            # Flask app factory (create_app), config, schema migration
│   ├── initialize.py      # Registers blueprints
│   ├── models.py          # SQLAlchemy models (Client, ClientContact, TeamMember)
│   ├── forms.py           # WTForms: ClientForm + contact/team row validators
│   ├── views/
│   │   ├── home.py        # Client directory (table & hierarchy views)
│   │   ├── clients.py     # Client CRUD routes
│   │   └── auth.py        # (placeholder)
│   ├── templates/         # Jinja2 templates (base, form, view, index)
│   └── static/            # app.js, app.css, structured.css
├── tests/
│   └── test_app.py        # pytest suite (uses in-memory SQLite)
├── instance/
│   └── clients.db         # Current client records (SQLite source for seeding)
├── pyproject.toml         # Project metadata + dependencies (uv)
├── requirements.txt       # Legacy requirements list
├── .env.example           # Environment template (copy to .env)
└── .env                   # Local secrets (gitignored, not committed)
```

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) (recommended package manager)
- A running MySQL/MariaDB server (e.g. via Podman) for production

## Development setup

### 1. Create the virtual environment and install dependencies

```bash
uv sync
```

If you don't have `uv`, install from `requirements.txt`:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and update the values:

```bash
cp .env.example .env
```

Key settings in `.env`:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask secret — use a long random value |
| `DB_NAME` | MySQL/MariaDB database name |
| `DB_USER` / `DB_PASS` | MySQL credentials |
| `DB_HOST` / `DB_PORT` | MySQL host and port (default `localhost` / `3306`) |

### 3. Create the MySQL database (MariaDB/MySQL server)

```sql
CREATE DATABASE ez_clients CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. Create the tables

```bash
uv run python create_tables.py
```

This creates `clients`, `client_contacts`, and `team_members` in MySQL. It is safe to re-run (uses `CREATE TABLE IF NOT EXISTS`).

### 5. Run the app

```bash
uv run python app.py
```

Open `http://127.0.0.1:5000`.

- With `.env` present, the app connects to MySQL via the `DB_*` values.
- If no database config is present, the app falls back to the bundled SQLite database (`instance/clients.db`) for quick evaluation.

## Seeding data

The repository ships current client records in `instance/clients.db` (SQLite). To copy this data into MySQL:

```bash
uv run python create_tables.py   # ensure tables exist (once)
uv run python seeder.py          # SQLite → MySQL
```

The seeder copies the `clients`, `client_contacts`, and `team_members` tables directly, preserving IDs so related records stay linked. It prints the number of rows copied per table and can read from a different source with `--source`:

```bash
uv run python seeder.py --source /path/to/clients.db
```

## Tests

```bash
uv run pytest
```

The test suite uses an in-memory SQLite database, so no MySQL server is required to run it.

## Notes

`instance/clients.db` contains real client and contact information. Because this repository is public, review the included data before sharing the repository URL more broadly.
