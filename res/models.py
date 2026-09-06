from datetime import datetime, timezone

from peewee import (
    CharField,
    DatabaseProxy,
    DateField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
)

db = DatabaseProxy()


class BaseModel(Model):
    class Meta:
        database = db


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


class Client(BaseModel):
    id = IntegerField(primary_key=True)
    name = CharField(180, null=False)
    status = CharField(10, null=False, default="active")
    website = CharField(255, null=True)
    industry = CharField(120, null=True)
    client_since = DateField(null=True)
    work_cycle = CharField(80, null=True)
    accounting_software = CharField(255, null=True)
    marketing_software = CharField(500, null=True)
    accounting_method = CharField(120, null=True)
    document_storage = CharField(255, null=True)
    contracted_hours = CharField(80, null=True)
    service_level = CharField(255, null=True)
    statement_of_work_url = CharField(500, null=True)
    sop_url = CharField(500, null=True)
    sop_url_label = CharField(120, null=True)
    sop_url_secondary = CharField(500, null=True)
    sop_url_secondary_label = CharField(120, null=True)
    systems_url = CharField(500, null=True)
    time_zone = CharField(120, null=True)
    address = CharField(500, null=True)
    business_hours = CharField(255, null=True)
    time_check_url = CharField(500, null=True)
    preferred_contact_method = CharField(120, null=True)
    weekly_meeting = CharField(255, null=True)
    monthly_financial_review = CharField(255, null=True)
    response_time_expectation = CharField(255, null=True)
    schedule_mode = CharField(20, null=False, default="shared")
    shared_work_days = CharField(120, null=True)
    shared_start_time = CharField(10, null=True)
    shared_end_time = CharField(10, null=True)
    created_at = DateTimeField(null=True, default=lambda: datetime.now(timezone.utc))
    updated_at = DateTimeField(null=True, default=lambda: datetime.now(timezone.utc))

    class Meta:
        table_name = "clients"


class ClientContact(BaseModel):
    id = IntegerField(primary_key=True)
    client = ForeignKeyField(Client, backref="contacts", column_name="client_id", on_delete="CASCADE")
    role = CharField(120, null=True)
    name = CharField(180, null=False)
    email = CharField(255, null=True)
    phone = CharField(80, null=True)
    position = IntegerField(null=False, default=0)

    class Meta:
        table_name = "client_contacts"


class TeamMember(BaseModel):
    id = IntegerField(primary_key=True)
    client = ForeignKeyField(Client, backref="team_members", column_name="client_id", on_delete="CASCADE")
    role = CharField(120, null=True)
    name = CharField(180, null=False)
    email = CharField(255, null=True)
    work_days = CharField(120, null=True)
    start_time = CharField(10, null=True)
    end_time = CharField(10, null=True)
    position = IntegerField(null=False, default=0)

    class Meta:
        table_name = "team_members"

    @property
    def schedule_text(self):
        return format_schedule(self.work_days, self.start_time, self.end_time)


ALL_MODELS = [Client, ClientContact, TeamMember]
