import sqlite3

import pytest

from tabletime.db import get_db, init_db


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


def test_init_db_runs_again_over_existing_data(app):
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO study_sessions (user_id, clock_in) VALUES (3, '2027-02-15T23:00:00Z')")
        db.commit()
        init_db()
        assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
        assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_init_db_command(runner, monkeypatch):
    called = []
    monkeypatch.setattr("tabletime.db.init_db", lambda: called.append(True))
    result = runner.invoke(args=["init-db"])
    assert "Initialized" in result.output
    assert called


def test_an_athlete_cannot_have_two_open_sessions(app):
    with app.app_context():
        db = get_db()
        db.execute("INSERT INTO study_sessions (user_id, clock_in) VALUES (3, '2027-02-15T23:00:00Z')")
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO study_sessions (user_id, clock_in) VALUES (3, '2027-02-15T23:10:00Z')")
        # A different athlete can be open at the same time.
        db.execute("INSERT INTO study_sessions (user_id, clock_in) VALUES (4, '2027-02-15T23:10:00Z')")


def test_clock_out_must_come_after_clock_in(app):
    with app.app_context():
        with pytest.raises(sqlite3.IntegrityError):
            get_db().execute(
                "INSERT INTO study_sessions (user_id, clock_in, clock_out)"
                " VALUES (3, '2027-02-15T23:00:00Z', '2027-02-15T22:00:00Z')")
