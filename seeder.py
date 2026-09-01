import argparse
import sqlite3
from datetime import date, datetime

from models import Client, ClientContact, TeamMember, db
from res.main import create_app


def read_clients(source_path):
    conn = sqlite3.connect(source_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM clients ORDER BY id")
    clients = [dict(row) for row in cur.fetchall()]

    cur.execute("SELECT * FROM client_contacts ORDER BY client_id, position")
    all_contacts = [dict(row) for row in cur.fetchall()]

    cur.execute("SELECT * FROM team_members ORDER BY client_id, position")
    all_team = [dict(row) for row in cur.fetchall()]

    conn.close()

    contacts_by_client = {}
    for c in all_contacts:
        cid = c.pop("client_id")
        contacts_by_client.setdefault(cid, []).append(c)

    team_by_client = {}
    for t in all_team:
        cid = t.pop("client_id")
        team_by_client.setdefault(cid, []).append(t)

    return clients, contacts_by_client, team_by_client


def parse_date(val):
    if not val:
        return None
    return date.fromisoformat(val)


def parse_datetime(val):
    if not val:
        return None
    return datetime.fromisoformat(val)


def seed_database(source_path):
    app = create_app()
    clients, contacts_map, team_map = read_clients(source_path)

    seeded = skipped = contacts_seeded = team_seeded = 0

    with app.app_context():
        existing = {c.name for c in Client.query.all()}
        for raw in clients:
            name = raw["name"]
            if name in existing:
                print(f"  Skipping (exists): {name}")
                skipped += 1
                continue

            client = Client(
                name=name,
                status=raw.get("status", "active"),
                website=raw.get("website"),
                industry=raw.get("industry"),
                client_since=parse_date(raw.get("client_since")),
                work_cycle=raw.get("work_cycle"),
                accounting_software=raw.get("accounting_software"),
                marketing_software=raw.get("marketing_software"),
                accounting_method=raw.get("accounting_method"),
                document_storage=raw.get("document_storage"),
                contracted_hours=raw.get("contracted_hours"),
                service_level=raw.get("service_level"),
                statement_of_work_url=raw.get("statement_of_work_url"),
                sop_url=raw.get("sop_url"),
                sop_url_label=raw.get("sop_url_label"),
                sop_url_secondary=raw.get("sop_url_secondary"),
                sop_url_secondary_label=raw.get("sop_url_secondary_label"),
                systems_url=raw.get("systems_url"),
                time_zone=raw.get("time_zone"),
                address=raw.get("address"),
                business_hours=raw.get("business_hours"),
                time_check_url=raw.get("time_check_url"),
                preferred_contact_method=raw.get("preferred_contact_method"),
                weekly_meeting=raw.get("weekly_meeting"),
                monthly_financial_review=raw.get("monthly_financial_review"),
                response_time_expectation=raw.get("response_time_expectation"),
                schedule_mode=raw.get("schedule_mode", "shared"),
                shared_work_days=raw.get("shared_work_days"),
                shared_start_time=raw.get("shared_start_time"),
                shared_end_time=raw.get("shared_end_time"),
                created_at=parse_datetime(raw.get("created_at")) or datetime.utcnow(),
                updated_at=parse_datetime(raw.get("updated_at")) or datetime.utcnow(),
            )
            db.session.add(client)
            db.session.flush()

            for c in contacts_map.get(raw["id"], []):
                db.session.add(ClientContact(
                    client_id=client.id,
                    role=c.get("role"),
                    name=c["name"],
                    email=c.get("email"),
                    phone=c.get("phone"),
                    position=c.get("position", 0),
                ))
                contacts_seeded += 1

            for t in team_map.get(raw["id"], []):
                db.session.add(TeamMember(
                    client_id=client.id,
                    role=t.get("role"),
                    name=t["name"],
                    email=t.get("email"),
                    work_days=t.get("work_days"),
                    start_time=t.get("start_time"),
                    end_time=t.get("end_time"),
                    position=t.get("position", 0),
                ))
                team_seeded += 1

            seeded += 1
            print(f"  Seeded: {name}")

        db.session.commit()

    print(f"\nDone: {seeded} clients, {contacts_seeded} contacts, {team_seeded} team members seeded. {skipped} skipped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed database from clients.db")
    parser.add_argument("--source", default="instance/clients.db", help="Path to source SQLite database")
    args = parser.parse_args()
    print(f"Seeding from {args.source}...")
    seed_database(args.source)
