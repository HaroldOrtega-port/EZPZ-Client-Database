from datetime import date, datetime, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for

from models import Client, ClientContact, TeamMember, db
from res.main import CLIENT_FIELDS

bp = Blueprint("clients", __name__)


@bp.route("/clients/new", methods=["GET", "POST"])
def create_client():
    client = Client()
    if request.method == "POST" and save_client(client):
        db.session.add(client)
        db.session.commit()
        flash("Client profile created.", "success")
        return redirect(url_for("clients.view_client", client_id=client.id))
    return render_template("form.html", client=None)


@bp.get("/clients/<int:client_id>")
def view_client(client_id):
    return render_template("view.html", client=db.get_or_404(Client, client_id))


@bp.route("/clients/<int:client_id>/edit", methods=["GET", "POST"])
def edit_client(client_id):
    client = db.get_or_404(Client, client_id)
    if request.method == "POST" and save_client(client):
        db.session.commit()
        flash("Client profile updated.", "success")
        return redirect(url_for("clients.view_client", client_id=client.id))
    return render_template("form.html", client=client)


@bp.post("/clients/<int:client_id>/delete")
def delete_client(client_id):
    db.session.delete(db.get_or_404(Client, client_id))
    db.session.commit()
    flash("Client profile deleted.", "success")
    return redirect(url_for("home.index"))


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
    raw_date = request.form.get("client_since", "")
    try:
        client.client_since = date.fromisoformat(raw_date) if raw_date else None
    except ValueError:
        flash("Client since must be a valid date.", "error")
        return False
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
