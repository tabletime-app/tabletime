-- The shared tables. Running `flask --app tabletime init-db` executes this file
-- first, then each part's schema.sql (scan, athlete, coach, admin).
-- It deletes all data.
--
-- Changes to this file affect every part of the app, so they go through a
-- pull request that the whole group agrees on.

DROP TABLE IF EXISTS study_sessions;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS teams;

CREATE TABLE teams (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    email         TEXT NOT NULL UNIQUE,       -- stored lowercase
    name          TEXT NOT NULL,
    password_hash TEXT NOT NULL,              -- never the password itself; used once logins exist
    role          TEXT NOT NULL CHECK (role IN ('athlete', 'coach', 'admin')),
    student_id    TEXT UNIQUE,                -- athletes only
    team_id       INTEGER REFERENCES teams (id),  -- athletes and coaches
    created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- One row per visit to the study table. Times are UTC text, for example
-- '2027-02-15T23:05:00Z' (see tabletime/times.py). A session with no
-- clock_out is still open: the athlete is at the table now.
CREATE TABLE study_sessions (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id   INTEGER NOT NULL REFERENCES users (id),
    clock_in  TEXT NOT NULL,
    clock_out TEXT,
    CHECK (clock_out IS NULL OR clock_out > clock_in)
);

-- An athlete can't have two open sessions at once. The database enforces
-- this, so it holds even when two requests arrive at the same moment.
CREATE UNIQUE INDEX one_open_session ON study_sessions (user_id) WHERE clock_out IS NULL;

CREATE INDEX sessions_by_user ON study_sessions (user_id, clock_in);
