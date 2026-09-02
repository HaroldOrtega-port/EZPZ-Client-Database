import argparse
import os
import sqlite3

import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.getenv("DB_NAME", "ez_clients")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))

TABLES = ("clients", "client_contacts", "team_members")


def copy_table(sqlite_conn, mysql_conn, table):
    sqlite_cur = sqlite_conn.cursor()
    mysql_cur = mysql_conn.cursor()

    sqlite_cur.execute(f"SELECT * FROM {table}")
    rows = sqlite_cur.fetchall()
    columns = [description[0] for description in sqlite_cur.description]

    placeholders = ", ".join(["%s"] * len(columns))
    column_sql = ", ".join(columns)
    insert_sql = f"INSERT INTO {table} ({column_sql}) VALUES ({placeholders})"

    mysql_cur.executemany(insert_sql, rows)
    mysql_conn.commit()
    return len(rows)


def main():
    parser = argparse.ArgumentParser(
        description="Copy data from the instance SQLite database to MySQL."
    )
    parser.add_argument("--source", default="instance/clients.db", help="Path to source SQLite database")
    args = parser.parse_args()

    sqlite_conn = sqlite3.connect(args.source)
    mysql_conn = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset="utf8mb4",
    )

    for table in TABLES:
        count = copy_table(sqlite_conn, mysql_conn, table)
        print(f"  {table}: {count} rows copied")

    sqlite_conn.close()
    mysql_conn.close()


if __name__ == "__main__":
    main()
