import os
from datetime import date, datetime, timezone

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

load_dotenv()
db = SQLAlchemy()


class Client(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False, index=True)
    status = db.Column(db.String(10), nullable=False, default="active", index=True)
    website = db.Column(db.String(255))
    industry = db.Column(db.String(120))
    client_since = db.Column(db.Date)
    onboarding_date = db.Column(db.Date)
    billing = db.Column(db.String(40))
    work_cycle = db.Column(db.String(80))
    accounting_software = db.Column(db.String(255))
    marketing_software = db.Column(db.String(500))
    accounting_method = db.Column(db.String(120))
    document_storage = db.Column(db.String(255))
    contracted_hours = db.Column(db.String(80))
    service_level = db.Column(db.String(255))
    statement_of_work_url = db.Column(db.String(500))
    sop_url = db.Column(db.String(500))
    sop_url_label = db.Column(db.String(120))
    sop_url_secondary = db.Column(db.String(500))
    sop_url_secondary_label = db.Column(db.String(120))
    systems_url = db.Column(db.String(500))
    time_zone = db.Column(db.String(120))
    address = db.Column(db.String(500))
    business_hours = db.Column(db.String(255))
    time_check_url = db.Column(db.String(500))
    preferred_contact_method = db.Column(db.String(120))
    weekly_meeting = db.Column(db.String(255))
    monthly_financial_review = db.Column(db.String(255))
    response_time_expectation = db.Column(db.String(255))
    schedule_mode = db.Column(db.String(20), nullable=False, default="shared")
    shared_work_days = db.Column(db.String(120))
    shared_start_time = db.Column(db.String(10))
    shared_end_time = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    contacts = db.relationship("ClientContact", cascade="all, delete-orphan", backref="client", order_by="ClientContact.position")
    team_members = db.relationship("TeamMember", cascade="all, delete-orphan", backref="client", order_by="TeamMember.position")


class ClientContact(db.Model):
    __tablename__ = "client_contacts"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    role = db.Column(db.String(120))
    name = db.Column(db.String(180), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(80))
    position = db.Column(db.Integer, nullable=False, default=0)


class TeamMember(db.Model):
    __tablename__ = "team_members"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False, index=True)
    role = db.Column(db.String(120))
    name = db.Column(db.String(180), nullable=False)
    email = db.Column(db.String(255))
    work_days = db.Column(db.String(120))
    start_time = db.Column(db.String(10))
    end_time = db.Column(db.String(10))
    position = db.Column(db.Integer, nullable=False, default=0)

    @property
    def schedule_text(self):
        return format_schedule(self.work_days, self.start_time, self.end_time)


def format_clock(value):
    if not value:
        return ""
    try:
        return datetime.strptime(value, "%H:%M").strftime("%I:%M %p").lstrip("0").replace(":00", "")
    except ValueError:
        return value


def format_schedule(days, start, end):
    days = format_work_days(days)
    times = " - ".join(part for part in (format_clock(start), format_clock(end)) if part)
    return " ".join(part for part in (days or "", times) if part) or "—"


def format_work_days(value):
    if not value or "," not in value:
        return value or ""
    ordered = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    selected = [day for day in ordered if day in value.split(",")]
    if not selected:
        return ""
    runs, start, previous = [], selected[0], selected[0]
    for day in selected[1:]:
        if ordered.index(day) == ordered.index(previous) + 1:
            previous = day
            continue
        runs.append(start if start == previous else f"{start}-{previous}")
        start = previous = day
    runs.append(start if start == previous else f"{start}-{previous}")
    return ", ".join(runs)


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


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-only-change-me"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///clients.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    if test_config:
        app.config.update(test_config)
    db.init_app(app)

    @app.context_processor
    def shared_form_options():
        return {"time_options": TIME_OPTIONS}

    @app.template_filter("date")
    def format_date(value):
        return value.strftime("%b %d, %Y") if value else ""

    @app.template_filter("schedule")
    def schedule_filter(values):
        return format_schedule(*values)

    @app.get("/")
    def index():
        query = request.args.get("q", "").strip()
        view_mode = request.args.get("view", "table")
        if view_mode not in {"tree", "table"}:
            view_mode = "table"
        statement = Client.query.order_by(Client.name.asc())
        if query and view_mode == "tree":
            statement = statement.filter(Client.name.ilike(f"%{query}%"))
        clients = statement.all()
        return render_template("index.html", clients=clients, active_clients=[c for c in clients if c.status == "active"], inactive_clients=[c for c in clients if c.status == "inactive"], query=query, view_mode=view_mode)

    @app.route("/clients/new", methods=["GET", "POST"])
    def create_client():
        client = Client()
        if request.method == "POST" and save_client(client):
            db.session.add(client)
            db.session.commit()
            flash("Client profile created.", "success")
            return redirect(url_for("view_client", client_id=client.id))
        return render_template("form.html", client=None)

    @app.get("/clients/<int:client_id>")
    def view_client(client_id):
        return render_template("view.html", client=db.get_or_404(Client, client_id))

    @app.route("/clients/<int:client_id>/edit", methods=["GET", "POST"])
    def edit_client(client_id):
        client = db.get_or_404(Client, client_id)
        if request.method == "POST" and save_client(client):
            db.session.commit()
            flash("Client profile updated.", "success")
            return redirect(url_for("view_client", client_id=client.id))
        return render_template("form.html", client=client)

    @app.post("/clients/<int:client_id>/delete")
    def delete_client(client_id):
        db.session.delete(db.get_or_404(Client, client_id))
        db.session.commit()
        flash("Client profile deleted.", "success")
        return redirect(url_for("index"))

    def save_client(client):
        name = request.form.get("name", "").strip()
        status = request.form.get("status", "active")
        if not name:
            flash("Client name is required.", "error")
            return False
        if status not in {"active", "inactive"}:
            flash("Choose a valid status.", "error")
            return False
        client.name, client.status = name, status
        for field in CLIENT_FIELDS:
            setattr(client, field, request.form.get(field, "").strip() or None)
        for field, label in (("client_since", "Client since"), ("onboarding_date", "Onboarding date")):
            raw_date = request.form.get(field, "")
            try:
                setattr(client, field, date.fromisoformat(raw_date) if raw_date else None)
            except ValueError:
                flash(f"{label} must be a valid date.", "error")
                return False
        billing = request.form.get("billing", "").strip()
        valid_billing = {"auto_ach", "auto_credit_card", "client_manual_payment"}
        if billing and billing not in valid_billing:
            flash("Choose a valid billing option.", "error")
            return False
        client.billing = billing or None
        client.contacts = build_people(ClientContact, "contact", include_phone=True)
        schedule_mode = request.form.get("schedule_mode", "shared")
        client.schedule_mode = schedule_mode if schedule_mode in {"shared", "individual"} else "shared"
        client.shared_work_days = request.form.get("shared_work_days", "").strip() or None
        client.shared_start_time = request.form.get("shared_start_time", "").strip() or None
        client.shared_end_time = request.form.get("shared_end_time", "").strip() or None
        client.team_members = build_people(TeamMember, "team", include_phone=False)
        client.updated_at = datetime.now(timezone.utc)
        return True

    def build_people(model, prefix, include_phone):
        names = request.form.getlist(f"{prefix}_name[]")
        roles = request.form.getlist(f"{prefix}_role[]")
        emails = request.form.getlist(f"{prefix}_email[]")
        phones = request.form.getlist(f"{prefix}_phone[]") if include_phone else []
        work_days = request.form.getlist(f"{prefix}_work_days[]") if prefix == "team" else []
        start_times = request.form.getlist(f"{prefix}_start_time[]") if prefix == "team" else []
        end_times = request.form.getlist(f"{prefix}_end_time[]") if prefix == "team" else []
        people = []
        for index, raw_name in enumerate(names):
            name = raw_name.strip()
            if not name:
                continue
            values = dict(name=name, role=value_at(roles, index), email=value_at(emails, index), position=index)
            if include_phone:
                values["phone"] = value_at(phones, index)
            if prefix == "team":
                values.update(work_days=value_at(work_days, index), start_time=value_at(start_times, index), end_time=value_at(end_times, index))
            people.append(model(**values))
        return people

    def value_at(values, index):
        return values[index].strip() or None if index < len(values) else None

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
            "onboarding_date": "DATE",
            "billing": "VARCHAR(40)",
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


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "true").lower() == "true")
