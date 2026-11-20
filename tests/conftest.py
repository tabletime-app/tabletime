"""Shared test setup: a fresh database for every test, with a few known users."""
import os
import tempfile

import pytest

from tabletime import create_app
from tabletime.db import add_user, get_db, init_db

PASSWORD = "password"


@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({"TESTING": True, "DATABASE": db_path, "SECRET_KEY": "test"})

    with app.app_context():
        init_db()
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

    yield app

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


class Forms:
    """Submit forms the way a browser would, including the CSRF token."""

    def __init__(self, client):
        self._client = client

    def post(self, url, data=None, **kwargs):
        with self._client.session_transaction() as sess:
            token = sess.setdefault("csrf_token", "test-csrf-token")
        return self._client.post(url, data={**(data or {}), "csrf_token": token}, **kwargs)

    def login(self, email="athlete@example.edu", password=PASSWORD):
        return self.post("/auth/login", {"email": email, "password": password})

    def logout(self):
        return self.post("/auth/logout")


@pytest.fixture
def forms(client):
    return Forms(client)
