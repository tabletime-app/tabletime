"""Database connection and command-line commands.

Every request gets its own SQLite connection, stored on Flask's `g` object
and closed when the request ends.

Timestamps are stored as UTC text in ISO 8601 form, for example
"2027-02-15T23:05:00Z". Convert to local time only when displaying
(see tabletime/times.py).
"""
import importlib
import random
import sqlite3
from datetime import datetime, time, timedelta

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

from . import times
from .times import local_zone, to_text

# The four parts of the app. init-db runs the shared schema.sql first, then
# each part's schema.sql in this order, and seed calls each part's seed(db)
# function, if it has one, after the shared fake data is in place.
PARTS = ["scan", "athlete", "coach", "admin"]
PART_SCHEMAS = [f"{part}/schema.sql" for part in PARTS]


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
    """Delete all data and create every table, shared tables first."""
    db = get_db()
    # Foreign keys are switched off while tables are dropped and re-created, so
    # the order of the DROP statements across files doesn't matter.
    db.execute("PRAGMA foreign_keys = OFF")
    for path in ["schema.sql", *PART_SCHEMAS]:
        with current_app.open_resource(path) as f:
            db.executescript(f.read().decode("utf8"))
    db.execute("PRAGMA foreign_keys = ON")


def add_user(db, *, email, name, role, password=None, password_hash=None,
             student_id=None, team_id=None):
    """Insert a user and return the new id. Raises sqlite3.IntegrityError on duplicates.

    Pass either the password, which is hashed here, or a hash made earlier.
    """
    if password_hash is None:
        password_hash = generate_password_hash(password)
    cur = db.execute(
        "INSERT INTO users (email, name, password_hash, role, student_id, team_id)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (email.strip().lower(), name.strip(), password_hash, role, student_id, team_id),
    )
    return cur.lastrowid


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Delete all data and create empty tables."""
    init_db()
    click.echo("Initialized the database.")


TEAMS = ["Soccer", "Basketball", "Swimming", "Track"]
ATHLETES_PER_TEAM = 8
SEED_WEEKS = 10
# Hours per week each athlete aims for. Most land near a typical 6-hour
# minimum; a few are well above or well below it, so reports have variety.
WEEKLY_HOURS = [2, 4, 5, 6, 6, 7, 8, 10]


def seed_sessions(db, athlete_ids, now=None, rng=None):
    """Add fake study sessions for the last SEED_WEEKS weeks and this week so far.

    Sessions fall on Sunday to Thursday evenings between 6 and 10 pm local
    time and are stored in UTC. This week only gets sessions that ended at
    least two hours before now, so the "this week" pages have data. A few
    athletes also get a session that is open right now. Returns the number
    of sessions added.
    """
    rng = rng or random.Random(253)
    zone = local_zone()
    now = now or times.utc_now()
    today = now.astimezone(zone).date()
    this_monday = today - timedelta(days=today.weekday())
    first_monday = this_monday - timedelta(weeks=SEED_WEEKS)
    latest_end = now - timedelta(hours=2)

    rows = []
    for user_id in athlete_ids:
        target = rng.choice(WEEKLY_HOURS)
        week = first_monday
        while week <= this_monday:
            goal_minutes = max(0, rng.gauss(target * 60, 45))
            evenings = [week + timedelta(days=d) for d in (0, 1, 2, 3, 6)]
            rng.shuffle(evenings)
            done = 0
            for day in evenings:
                if done >= goal_minutes:
                    break
                length = rng.choice([45, 60, 75, 90, 120, 150])
                start = datetime.combine(day, time(18, 0), zone) + timedelta(
                    minutes=rng.randrange(0, 120, 5))
                end = start + timedelta(minutes=length)
                if end > latest_end:
                    continue  # this week's sessions stop before now
                rows.append((user_id, to_text(start), to_text(end)))
                done += length
            week += timedelta(weeks=1)

    # A few athletes are at the table right now, with sessions still open.
    for user_id in rng.sample(athlete_ids, k=min(3, len(athlete_ids))):
        start = now - timedelta(minutes=rng.randrange(10, 90, 5))
        rows.append((user_id, to_text(start), None))

    db.executemany(
        "INSERT INTO study_sessions (user_id, clock_in, clock_out) VALUES (?, ?, ?)", rows)
    return len(rows)


@click.command("seed")
@with_appcontext
def seed_command():
    """Add fake teams, users and study sessions. Every password is "password"."""
    db = get_db()
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0]:
        click.echo("The database already has users. Run init-db first to start over.")
        return

    # Hashing is slow on purpose, so hash the shared fake password once.
    hashed = generate_password_hash("password")
    add_user(db, email="admin@example.edu", name="Ada Admin", password_hash=hashed, role="admin")
    athlete_ids = []
    for i, team in enumerate(TEAMS, start=1):
        team_id = db.execute("INSERT INTO teams (name) VALUES (?)", (team,)).lastrowid
        add_user(db, email=f"coach{i}@example.edu", name=f"{team} Coach", password_hash=hashed,
                 role="coach", team_id=team_id)
        for j in range(1, ATHLETES_PER_TEAM + 1):
            n = i * 10 + j
            athlete_ids.append(add_user(
                db, email=f"athlete{n}@example.edu", name=f"Athlete {n}", password_hash=hashed,
                role="athlete", student_id=f"10000{n}", team_id=team_id))

    sessions = seed_sessions(db, athlete_ids)
    seeded_parts = seed_parts(db)
    db.commit()
    click.echo(f"Added {len(TEAMS)} teams, {len(TEAMS) + 1 + len(athlete_ids)} users "
               f"and {sessions} study sessions.")
    for part in seeded_parts:
        click.echo(f"Ran the {part} part's seed function.")


def seed_parts(db):
    """Call seed(db) in each part's package, if the part defines one.

    A part adds fake rows for its own tables this way, for example the
    admin part's open hours or the coach part's team minimums, once the
    shared teams and users exist. Returns the names of the parts that ran.
    """
    ran = []
    for part in PARTS:
        module = importlib.import_module(f"tabletime.{part}")
        if hasattr(module, "seed"):
            module.seed(db)
            ran.append(part)
    return ran


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_command)
