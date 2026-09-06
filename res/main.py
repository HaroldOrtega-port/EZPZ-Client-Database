import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask
from peewee import MySQLDatabase

from res.models import Client, TeamMember, db, ALL_MODELS

load_dotenv()

TIME_OPTIONS = []
for hour in range(24):
    for minute in (0, 30):
        value = f"{hour:02d}:{minute:02d}"
        label = datetime.strptime(value, "%H:%M").strftime("%I:%M %p").lstrip("0")
        TIME_OPTIONS.append((value, label))


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-only-change-me"),
    )
    if test_config:
        app.config.update(test_config)

    if test_config and "DATABASE" in test_config:
        database = test_config["DATABASE"]
    else:
        database = MySQLDatabase(
            os.getenv("DB_NAME", "ez_clients"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASS", ""),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            charset="utf8mb4",
        )
    db.initialize(database)
    database.connect(reuse_if_open=True)
    database.create_tables(ALL_MODELS)

    from res.initialize import routes
    routes(app)

    @app.context_processor
    def shared_form_options():
        return {"time_options": TIME_OPTIONS}

    @app.template_filter("date")
    def format_date(value):
        return value.strftime("%b %d, %Y") if value else ""

    @app.template_filter("schedule")
    def schedule_filter(values):
        from res.models import format_schedule
        return format_schedule(*values)

    if not (test_config and test_config.get("TESTING")):
        ensure_schedule_columns()
    return app


def ensure_schedule_columns():
    """Add schedule fields to databases created by earlier app versions."""
    additions = {
        "clients": {
            "accounting_method": "VARCHAR(120)",
            "marketing_software": "VARCHAR(500)",
            "sop_url_label": "VARCHAR(120)",
            "sop_url_secondary": "VARCHAR(500)",
            "sop_url_secondary_label": "VARCHAR(120)",
            "schedule_mode": "VARCHAR(20) NOT NULL DEFAULT 'shared'",
            "shared_work_days": "VARCHAR(120)",
            "shared_start_time": "VARCHAR(10)",
            "shared_end_time": "VARCHAR(10)",
        },
        "team_members": {
            "work_days": "VARCHAR(120)",
            "start_time": "VARCHAR(10)",
            "end_time": "VARCHAR(10)",
        },
    }
    cursor = db.execute_sql("SHOW TABLES")
    table_names = {row[0] for row in cursor.fetchall()}

    for table_name, columns in additions.items():
        if table_name not in table_names:
            continue
        cursor = db.execute_sql(f"DESCRIBE {table_name}")
        existing = {row[0] for row in cursor.fetchall()}
        for column_name, definition in columns.items():
            if column_name not in existing:
                db.execute_sql(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")
