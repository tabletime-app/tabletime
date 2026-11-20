"""Database connection and command-line commands.

Every request gets its own SQLite connection, stored on Flask's `g` object
and closed when the request ends.

Timestamps are stored as UTC text in ISO 8601 form, for example
"2026-09-14T19:05:00Z". Convert to local time only when displaying.
"""
import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row  # rows act like dicts: row["email"]
        g.db.execute("PRAGMA foreign_keys = ON")  # SQLite leaves these off by default
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


def add_user(db, *, email, name, password, role, student_id=None, team_id=None):
    """Insert a user and return the new id. Raises sqlite3.IntegrityError on duplicates."""
    cur = db.execute(
        "INSERT INTO users (email, name, password_hash, role, student_id, team_id)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (email.strip().lower(), name.strip(), generate_password_hash(password),
         role, student_id, team_id),
    )
    return cur.lastrowid


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Delete all data and create empty tables."""
    init_db()
    click.echo("Initialized the database.")


@click.command("create-admin")
@with_appcontext
@click.argument("email")
@click.option("--name", default="Administrator", help="Display name.")
@click.password_option()
def create_admin_command(email, name, password):
    """Create an admin account."""
    db = get_db()
    try:
        add_user(db, email=email, name=name, password=password, role="admin")
        db.commit()
    except sqlite3.IntegrityError:
        raise click.ClickException(f"A user with email {email} already exists.")
    click.echo(f"Created admin {email}.")


@click.command("seed")
@with_appcontext
def seed_command():
    """Add fake teams and users for development. Every password is "password"."""
    db = get_db()
    teams = ["Soccer", "Basketball", "Swimming"]
    for team in teams:
        db.execute("INSERT OR IGNORE INTO teams (name) VALUES (?)", (team,))
    team_ids = {row["name"]: row["id"] for row in db.execute("SELECT id, name FROM teams")}

    people = [("admin@example.edu", "Ada Admin", "admin", None, None)]
    for i, team in enumerate(teams, start=1):
        people.append((f"coach{i}@example.edu", f"{team} Coach", "coach", None, team_ids[team]))
        for j in range(1, 6):
            n = i * 10 + j
            people.append((f"athlete{n}@example.edu", f"Athlete {n}", "athlete",
                           f"10000{n}", team_ids[team]))

    added = 0
    for email, name, role, student_id, team_id in people:
        try:
            add_user(db, email=email, name=name, password="password", role=role,
                     student_id=student_id, team_id=team_id)
            added += 1
        except sqlite3.IntegrityError:
            pass  # already seeded
    db.commit()
    click.echo(f"Added {added} users. Log in as admin@example.edu / password.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(seed_command)
