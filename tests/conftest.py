"""Shared test setup: a fresh database for every test, with a few known users."""
import os
import tempfile

import pytest

from tabletime import create_app
from tabletime.db import add_user, get_db, init_db

PASSWORD = "password"


@pytest.fixture
def empty_app():
    """An app with empty tables."""
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({"TESTING": True, "DATABASE": db_path, "SECRET_KEY": "test"})
    with app.app_context():
        init_db()
    yield app
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def app(empty_app):
    """An app with two teams, one admin, one coach and two athletes."""
    with empty_app.app_context():
        db = get_db()
        db.execute("INSERT INTO teams (name) VALUES ('Soccer'), ('Swimming')")  # ids 1 and 2
        add_user(db, email="admin@example.edu", name="Ada Admin", password=PASSWORD, role="admin")
        add_user(db, email="coach@example.edu", name="Cal Coach", password=PASSWORD,
                 role="coach", team_id=1)
        add_user(db, email="athlete@example.edu", name="Ari Athlete", password=PASSWORD,
                 role="athlete", student_id="1000001", team_id=1)
        add_user(db, email="swimmer@example.edu", name="Sam Swimmer", password=PASSWORD,
                 role="athlete", student_id="1000002", team_id=2)
        db.commit()
    return empty_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def act_as(app, client):
    """Pick a user from the Acting as menu, by email: act_as("coach@example.edu")."""
    def pick(email):
        with app.app_context():
            user_id = get_db().execute(
                "SELECT id FROM users WHERE email = ?", (email,)).fetchone()["id"]
        return client.post("/dev/act-as", data={"user_id": user_id})
    return pick


@pytest.fixture
def freeze_time(monkeypatch):
    """Fix the app's clock: freeze_time(datetime(2027, 2, 15, 23, 0, tzinfo=timezone.utc)).

    This replaces tabletime.times.utc_now, so now_text(), week_bounds() and
    any code that calls times.utc_now() see that moment. QR tokens are
    different: make_token() and check_token() read the system clock, so pass
    them the time explicitly, for example make_token(now=moment.timestamp())
    and check_token(token, now=moment.timestamp()).
    """
    def freeze(moment):
        monkeypatch.setattr("tabletime.times.utc_now", lambda: moment)
        return moment
    return freeze
