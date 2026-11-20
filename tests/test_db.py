import sqlite3

import pytest

from tabletime.db import get_db


def test_connection_is_reused_within_a_request(app):
    with app.app_context():
        assert get_db() is get_db()


def test_connection_closes_after_the_request(app):
    with app.app_context():
        db = get_db()
    with pytest.raises(sqlite3.ProgrammingError):
        db.execute("SELECT 1")


def test_foreign_keys_are_enforced(app):
    with app.app_context():
        with pytest.raises(sqlite3.IntegrityError):
            get_db().execute(
                "INSERT INTO users (email, name, password_hash, role, team_id)"
                " VALUES ('x@example.edu', 'X', 'hash', 'athlete', 999)")


def test_unknown_role_is_rejected(app):
    with app.app_context():
        with pytest.raises(sqlite3.IntegrityError):
            get_db().execute(
                "INSERT INTO users (email, name, password_hash, role)"
                " VALUES ('x@example.edu', 'X', 'hash', 'superuser')")


def test_passwords_are_stored_hashed(app):
    with app.app_context():
        row = get_db().execute(
            "SELECT password_hash FROM users WHERE email = 'athlete@example.edu'").fetchone()
        assert row["password_hash"] != "password"
        assert row["password_hash"].startswith(("scrypt:", "pbkdf2:"))


def test_init_db_command(runner, monkeypatch):
    called = []
    monkeypatch.setattr("tabletime.db.init_db", lambda: called.append(True))
    result = runner.invoke(args=["init-db"])
    assert "Initialized" in result.output
    assert called


def test_seed_command_can_run_twice(runner, app):
    first = runner.invoke(args=["seed"])
    second = runner.invoke(args=["seed"])
    assert first.exit_code == 0 and second.exit_code == 0
    assert "Added 0 users" in second.output
    with app.app_context():
        athletes = get_db().execute(
            "SELECT COUNT(*) FROM users WHERE role = 'athlete'").fetchone()[0]
        assert athletes == 2 + 15  # two from conftest, five per seeded team


def test_create_admin_rejects_duplicates(runner):
    result = runner.invoke(args=["create-admin", "admin@example.edu"], input="pw\npw\n")
    assert result.exit_code != 0
    assert "already exists" in result.output
