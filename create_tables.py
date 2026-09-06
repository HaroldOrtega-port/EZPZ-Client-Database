import os

from dotenv import load_dotenv
from peewee import MySQLDatabase

from models import Client, ClientContact, TeamMember, db

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "ez_clients")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))


def main():
    database = MySQLDatabase(
        DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT,
        charset="utf8mb4",
    )
    db.initialize(database)
    database.connect(reuse_if_open=True)
    database.create_tables([Client, ClientContact, TeamMember], safe=True)
    database.close()
    print(f"Tables created in {DB_NAME}: clients, client_contacts, team_members")


if __name__ == "__main__":
    main()
