from datetime import datetime

from peewee import (
    CharField,
    DateField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Model,
)

TEXT_FIELDS = (
    "website", "industry", "work_cycle", "accounting_software",
    "marketing_software", "accounting_method", "document_storage",
    "contracted_hours", "service_level", "statement_of_work_url",
    "sop_url", "sop_url_label", "sop_url_secondary", "sop_url_secondary_label",
    "systems_url", "time_zone", "address", "business_hours", "time_check_url",
    "preferred_contact_method", "weekly_meeting", "monthly_financial_review",
    "response_time_expectation", "shared_work_days", "shared_start_time",
    "shared_end_time",
)

_TEXT_DEFAULTS = {
    "website": 255, "industry": 120, "work_cycle": 80,
    "accounting_software": 255, "marketing_software": 500,
    "accounting_method": 120, "document_storage": 255, "contracted_hours": 80,
    "service_level": 255, "statement_of_work_url": 500, "sop_url": 500,
    "sop_url_label": 120, "sop_url_secondary": 500, "sop_url_secondary_label": 120,
    "systems_url": 500, "time_zone": 120, "address": 500, "business_hours": 255,
    "time_check_url": 500, "preferred_contact_method": 120, "weekly_meeting": 255,
    "monthly_financial_review": 255, "response_time_expectation": 255,
    "shared_work_days": 120, "shared_start_time": 10, "shared_end_time": 10,
}


def make_client_model(cls):
    attrs = {
        "id": IntegerField(primary_key=True),
        "name": CharField(180, null=False),
        "status": CharField(10, null=False, default="active"),
        "client_since": DateField(null=True),
        "schedule_mode": CharField(20, null=False, default="shared"),
        "created_at": DateTimeField(null=True, default=datetime.now),
        "updated_at": DateTimeField(null=True, default=datetime.now),
        "Meta": type("Meta", (), {"table_name": "clients"}),
    }
    for field in TEXT_FIELDS:
        attrs[field] = CharField(_TEXT_DEFAULTS.get(field, 255), null=True)
    return type("Client", (Model,), attrs)


def make_contact_model(cls):
    return type(
        "ClientContact",
        (Model,),
        {
            "id": IntegerField(primary_key=True),
            "client": ForeignKeyField(cls, backref="contacts", column_name="client_id", on_delete="CASCADE"),
            "role": CharField(120, null=True),
            "name": CharField(180, null=False),
            "email": CharField(255, null=True),
            "phone": CharField(80, null=True),
            "position": IntegerField(null=False, default=0),
            "Meta": type("Meta", (), {"table_name": "client_contacts"}),
        },
    )


def make_team_model(cls):
    return type(
        "TeamMember",
        (Model,),
        {
            "id": IntegerField(primary_key=True),
            "client": ForeignKeyField(cls, backref="team_members", column_name="client_id", on_delete="CASCADE"),
            "role": CharField(120, null=True),
            "name": CharField(180, null=False),
            "email": CharField(255, null=True),
            "work_days": CharField(120, null=True),
            "start_time": CharField(10, null=True),
            "end_time": CharField(10, null=True),
            "position": IntegerField(null=False, default=0),
            "Meta": type("Meta", (), {"table_name": "team_members"}),
        },
    )


def build_models(database):
    """Build Client, ClientContact, TeamMember bound to *database*."""
    Client = make_client_model(None)
    Client._meta.database = database
    ClientContact = make_contact_model(Client)
    ClientContact._meta.database = database
    TeamMember = make_team_model(Client)
    TeamMember._meta.database = database
    return Client, ClientContact, TeamMember
