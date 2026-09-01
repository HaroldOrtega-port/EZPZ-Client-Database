from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def format_clock(value):
    if not value:
        return ""
    try:
        return datetime.strptime(value, "%H:%M").strftime("%I:%M %p").lstrip("0").replace(":00", "")
    except ValueError:
        return value


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


def format_schedule(days, start, end):
    days = format_work_days(days)
    times = " - ".join(part for part in (format_clock(start), format_clock(end)) if part)
    return " ".join(part for part in (days or "", times) if part) or "—"


class Client(db.Model):
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(180), nullable=False, index=True)
    status = db.Column(db.String(10), nullable=False, default="active", index=True)
    website = db.Column(db.String(255))
    industry = db.Column(db.String(120))
    client_since = db.Column(db.Date)
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
