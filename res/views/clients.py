from datetime import datetime, timezone

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from res.models import Client, ClientContact, TeamMember, db
from res.forms import ClientForm, build_people_from_form

bp = Blueprint("clients", __name__)


def get_or_404(model, obj_id):
    try:
        return model.get_by_id(obj_id)
    except model.DoesNotExist:
        abort(404)


@bp.route("/clients/new", methods=["GET", "POST"])
def create_client():
    client = Client()
    if request.method == "POST" and save_client(client):
        client.save()
        flash("Client profile created.", "success")
        return redirect(url_for("clients.view_client", client_id=client.id))
    return render_template("form.html", client=None)


@bp.get("/clients/<int:client_id>")
def view_client(client_id):
    return render_template("view.html", client=get_or_404(Client, client_id))


@bp.route("/clients/<int:client_id>/edit", methods=["GET", "POST"])
def edit_client(client_id):
    client = get_or_404(Client, client_id)
    if request.method == "POST" and save_client(client):
        client.save()
        flash("Client profile updated.", "success")
        return redirect(url_for("clients.view_client", client_id=client.id))
    return render_template("form.html", client=client)


@bp.post("/clients/<int:client_id>/delete")
def delete_client(client_id):
    client = get_or_404(Client, client_id)
    client.delete_instance(recursive=True)
    flash("Client profile deleted.", "success")
    return redirect(url_for("home.index"))


def save_client(client):
    form = ClientForm()
    if not form.validate_on_submit():
        for errors in form.errors.values():
            for error in errors:
                flash(error, "error")
        return False

    client.name = form.name.data
    client.status = form.status.data

    string_fields = [
        "website", "industry", "work_cycle", "accounting_software",
        "marketing_software", "accounting_method", "document_storage",
        "contracted_hours", "service_level", "statement_of_work_url",
        "sop_url", "sop_url_label", "sop_url_secondary",
        "sop_url_secondary_label", "systems_url", "time_zone", "address",
        "business_hours", "preferred_contact_method", "weekly_meeting",
        "monthly_financial_review", "response_time_expectation",
    ]
    for field in string_fields:
        setattr(client, field, getattr(form, field).data or None)

    client.client_since = form.client_since.data
    client.schedule_mode = form.schedule_mode.data or "shared"
    client.shared_work_days = form.shared_work_days.data or None
    client.shared_start_time = form.shared_start_time.data or None
    client.shared_end_time = form.shared_end_time.data or None

    contact_rows, contact_errors = build_people_from_form(
        form, "contact", include_phone=True
    )
    if contact_errors:
        flash("Each contact must have a name.", "error")
        return False

    team_rows, team_errors = build_people_from_form(form, "team")
    if team_errors:
        flash("Each team member must have a name.", "error")
        return False

    client.updated_at = datetime.now(timezone.utc)

    with db.atomic():
        client.save()

        if client.id:
            ClientContact.delete().where(ClientContact.client == client).execute()
            TeamMember.delete().where(TeamMember.client == client).execute()

        for i, r in enumerate(contact_rows):
            if r.name:
                ClientContact.create(
                    client=client,
                    name=r.name,
                    role=r.role,
                    email=r.email,
                    phone=r.phone,
                    position=i,
                )

        for i, r in enumerate(team_rows):
            if r.name:
                TeamMember.create(
                    client=client,
                    name=r.name,
                    role=r.role,
                    email=r.email,
                    work_days=r.work_days,
                    start_time=r.start_time,
                    end_time=r.end_time,
                    position=i,
                )

    return True
