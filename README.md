# EZPZ Client Database — Flask CRUD

A structured client-profile application with create, read, update, delete, Active/Inactive filtering, and unlimited key contacts and EZPZ team members.

## MySQL setup

```sql
CREATE DATABASE ekwips_clients CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'notes_user'@'localhost' IDENTIFIED BY 'change-me';
GRANT ALL PRIVILEGES ON ekwips_clients.* TO 'notes_user'@'localhost';
FLUSH PRIVILEGES;
```

Copy `.env.example` to `.env`, update the password and secret, then run:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`. Tables and three sample users are created automatically on first start. If `DATABASE_URL` is omitted, the app uses the included SQLite database for quick evaluation; production should use the provided MySQL URL.

## Included data

`instance/clients.db` contains the current client records used by the application. The legacy local `instance/notes.db`, environment files, dependency caches, test caches, and generated archives are intentionally excluded.

Because this repository is public, review the included client/contact information before sharing the repository URL more broadly.
