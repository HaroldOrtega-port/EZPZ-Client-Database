from flask_wtf import FlaskForm
from wtforms import DateField, RadioField, SelectField, StringField
from wtforms.validators import DataRequired, Optional, URL

from res.main import TIME_OPTIONS


def _strip(value):
    if isinstance(value, str):
        return value.strip()
    return value


class ClientForm(FlaskForm):
    name = StringField("Client name", validators=[DataRequired(message="Client name is required.")])
    status = SelectField(
        "Status",
        choices=[("active", "Active"), ("inactive", "Inactive")],
        validators=[DataRequired()],
    )
    website = StringField("Website", validators=[Optional()])
    industry = StringField("Industry", validators=[Optional()])
    client_since = DateField("Client since", validators=[Optional()], format="%Y-%m-%d")
    work_cycle = StringField("Work cycle", validators=[Optional()])
    accounting_software = StringField("Accounting software", validators=[Optional()])
    marketing_software = StringField("Marketing software", validators=[Optional()])
    accounting_method = StringField("Accounting method", validators=[Optional()])
    document_storage = StringField("Document storage", validators=[Optional()])
    contracted_hours = StringField("Contracted hours", validators=[Optional()])
    service_level = StringField("Service level", validators=[Optional()])
    statement_of_work_url = StringField(
        "Statement of Work URL", validators=[Optional(), URL()]
    )
    sop_url = StringField("Primary SOP URL", validators=[Optional(), URL()])
    sop_url_label = StringField("Primary SOP label", validators=[Optional()])
    sop_url_secondary = StringField(
        "Secondary SOP URL", validators=[Optional(), URL()]
    )
    sop_url_secondary_label = StringField("Secondary SOP label", validators=[Optional()])
    systems_url = StringField("Systems URL", validators=[Optional(), URL()])
    time_zone = SelectField(
        "Time zone",
        choices=[
            ("", "Select a time zone"),
            ("Eastern Time (ET)", "Eastern Time (ET)"),
            ("Central Time (CT)", "Central Time (CT)"),
            ("Mountain Time (MT)", "Mountain Time (MT)"),
            ("Pacific Time (PT)", "Pacific Time (PT)"),
        ],
        validators=[Optional()],
    )
    address = StringField("Address", validators=[Optional()])
    business_hours = StringField("Business hours", validators=[Optional()])
    preferred_contact_method = StringField(
        "Preferred contact method", validators=[Optional()]
    )
    weekly_meeting = StringField("Weekly meeting", validators=[Optional()])
    monthly_financial_review = StringField(
        "Monthly financial review", validators=[Optional()]
    )
    response_time_expectation = StringField(
        "Response time expectation", validators=[Optional()]
    )
    schedule_mode = RadioField(
        "Schedule mode",
        choices=[("shared", "Shared"), ("individual", "Individual")],
        default="shared",
        validators=[DataRequired()],
    )
    shared_work_days = StringField("Shared work days", validators=[Optional()])
    shared_start_time = SelectField(
        "Shared start time",
        choices=[("", "Select time")] + TIME_OPTIONS,
        validators=[Optional()],
    )
    shared_end_time = SelectField(
        "Shared end time",
        choices=[("", "Select time")] + TIME_OPTIONS,
        validators=[Optional()],
    )

    def validate_on_submit(self):
        valid = super().validate_on_submit()
        if self.name.data:
            self.name.data = self.name.data.strip()
        if self.status.data:
            self.status.data = self.status.data.strip()
        return valid


class ContactRowForm:
    """Validates a single contact row extracted from repeating form arrays."""

    def __init__(self, name, role=None, email=None, phone=None):
        self.name = _strip(name)
        self.role = _strip(role)
        self.email = _strip(email)
        self.phone = _strip(phone)
        self.errors = []

    @property
    def is_valid(self):
        self.errors = []
        if not self.name:
            self.errors.append("Contact name is required.")
        return len(self.errors) == 0


class TeamMemberRowForm:
    """Validates a single team member row extracted from repeating form arrays."""

    def __init__(
        self, name, role=None, email=None, work_days=None, start_time=None, end_time=None
    ):
        self.name = _strip(name)
        self.role = _strip(role)
        self.email = _strip(email)
        self.work_days = _strip(work_days)
        self.start_time = _strip(start_time)
        self.end_time = _strip(end_time)
        self.errors = []

    @property
    def is_valid(self):
        self.errors = []
        if not self.name:
            self.errors.append("Team member name is required.")
        return len(self.errors) == 0


def build_people_from_form(form, prefix, include_phone=False):
    """Extract repeating rows from request.form into a list of row forms.

    Returns (rows, has_errors). Each row is a ContactRowForm or
    TeamMemberRowForm depending on *prefix*.
    """
    from flask import request

    names = request.form.getlist(f"{prefix}_name[]")
    roles = request.form.getlist(f"{prefix}_role[]")
    emails = request.form.getlist(f"{prefix}_email[]")
    phones = request.form.getlist(f"{prefix}_phone[]") if include_phone else []
    work_days = request.form.getlist(f"{prefix}_work_days[]") if prefix == "team" else []
    start_times = (
        request.form.getlist(f"{prefix}_start_time[]") if prefix == "team" else []
    )
    end_times = (
        request.form.getlist(f"{prefix}_end_time[]") if prefix == "team" else []
    )

    def _at(lst, i):
        return lst[i].strip() if i < len(lst) and lst[i].strip() else None

    rows = []
    has_errors = False
    for i, raw_name in enumerate(names):
        if prefix == "team":
            row = TeamMemberRowForm(
                name=raw_name,
                role=_at(roles, i),
                email=_at(emails, i),
                work_days=_at(work_days, i),
                start_time=_at(start_times, i),
                end_time=_at(end_times, i),
            )
        else:
            row = ContactRowForm(
                name=raw_name,
                role=_at(roles, i),
                email=_at(emails, i),
                phone=_at(phones, i) if include_phone else None,
            )
        if raw_name.strip():
            if not row.is_valid:
                has_errors = True
        rows.append(row)

    return rows, has_errors
