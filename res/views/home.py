from flask import Blueprint, render_template, request

from models import Client

bp = Blueprint("home", __name__)


@bp.get("/")
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
