from collections import Counter
from datetime import datetime, timezone

from tabletime import times
from tabletime.db import ATHLETES_PER_TEAM, SEED_WEEKS, TEAMS, get_db
from tabletime.times import FORMAT, from_text


def run_seed(app):
    return app.test_cli_runner().invoke(args=["seed"])


def test_seed_adds_teams_and_users(empty_app):
    result = run_seed(empty_app)
    assert result.exit_code == 0
    with empty_app.app_context():
        roles = Counter(r["role"] for r in get_db().execute("SELECT role FROM users"))
    assert roles == {"admin": 1, "coach": len(TEAMS), "athlete": len(TEAMS) * ATHLETES_PER_TEAM}


def test_seed_refuses_to_run_twice(empty_app):
    run_seed(empty_app)
    result = run_seed(empty_app)
    assert "already has users" in result.output


def test_seeded_sessions_are_well_formed(empty_app):
    run_seed(empty_app)
    with empty_app.app_context():
        db = get_db()
        rows = db.execute(
            "SELECT s.*, u.role FROM study_sessions s JOIN users u ON u.id = s.user_id").fetchall()
        assert len(rows) > 500
        assert {r["role"] for r in rows} == {"athlete"}
        for r in rows:
            datetime.strptime(r["clock_in"], FORMAT)  # raises if not UTC text
            if r["clock_out"] is not None:
                assert from_text(r["clock_out"]) > from_text(r["clock_in"])
        open_sessions = [r for r in rows if r["clock_out"] is None]
        assert len(open_sessions) == 3
        athletes = db.execute("SELECT COUNT(*) FROM users WHERE role = 'athlete'").fetchone()[0]
        with_sessions = db.execute(
            "SELECT COUNT(DISTINCT user_id) FROM study_sessions").fetchone()[0]
        assert with_sessions == athletes


def test_seeded_hours_vary_around_six_a_week(empty_app):
    run_seed(empty_app)
    with empty_app.app_context():
        this_week, _ = times.week_bounds()
        weekly = get_db().execute("""
            SELECT user_id,
                   SUM((julianday(clock_out) - julianday(clock_in)) * 24) / ? AS hours
            FROM study_sessions WHERE clock_out IS NOT NULL AND clock_in < ?
            GROUP BY user_id""", (SEED_WEEKS, this_week)).fetchall()
    hours = [r["hours"] for r in weekly]
    assert min(hours) < 4 and max(hours) > 7.5
    assert any(5 <= h <= 7 for h in hours)


def test_this_week_has_sessions_but_none_in_the_future(empty_app, freeze_time):
    # Thursday evening in Central time, so this week has had several evenings.
    now = freeze_time(datetime(2027, 2, 19, 2, 0, tzinfo=timezone.utc))
    run_seed(empty_app)
    with empty_app.app_context():
        db = get_db()
        start, _ = times.week_bounds()
        this_week = db.execute(
            "SELECT COUNT(*) FROM study_sessions WHERE clock_in >= ?", (start,)).fetchone()[0]
        latest = db.execute("SELECT MAX(clock_in) FROM study_sessions").fetchone()[0]
        latest_out = db.execute("SELECT MAX(clock_out) FROM study_sessions").fetchone()[0]
    assert this_week > 20
    assert from_text(latest) <= now and from_text(latest_out) <= now


def test_seed_calls_each_parts_seed_function(empty_app, monkeypatch):
    import tabletime.admin
    calls = []
    monkeypatch.setattr(tabletime.admin, "seed", lambda db: calls.append(db), raising=False)
    result = run_seed(empty_app)
    assert len(calls) == 1
    assert "Ran the admin part's seed function." in result.output
