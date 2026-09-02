import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask
from sqlalchemy import inspect, text

from res.models import db, format_schedule

load_dotenv()

CLIENT_FIELDS = (
    "website", "industry", "work_cycle", "accounting_software", "marketing_software", "accounting_method", "document_storage",
    "contracted_hours", "service_level", "statement_of_work_url", "sop_url", "sop_url_label",
    "sop_url_secondary", "sop_url_secondary_label", "systems_url",
    "time_zone", "address", "business_hours", "preferred_contact_method",
    "weekly_meeting", "monthly_financial_review", "response_time_expectation",
)

TIME_OPTIONS = []
for hour in range(24):
    for minute in (0, 30):
        value = f"{hour:02d}:{minute:02d}"
        label = datetime.strptime(value, "%H:%M").strftime("%I:%M %p").lstrip("0")
        TIME_OPTIONS.append((value, label))


def database_uri():
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    if name and user:
        password = os.getenv("DB_PASS", "")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "3306")
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"
    return os.getenv("DATABASE_URL", "sqlite:///clients.db")


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-only-change-me"),
        SQLALCHEMY_DATABASE_URI=database_uri(),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)
    db.init_app(app)

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
        return format_schedule(*values)

    with app.app_context():
        db.create_all()
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
    schema = inspect(db.engine)
    for table_name, columns in additions.items():
        existing = {column["name"] for column in schema.get_columns(table_name)}
        for column_name, definition in columns.items():
            if column_name not in existing:
                db.session.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}"))
    db.session.commit()
