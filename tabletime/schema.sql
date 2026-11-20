-- Running `flask --app tabletime init-db` executes this file.
-- It deletes all data. Drop tables that reference others first.

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
    password_hash TEXT NOT NULL,              -- never the password itself
    role          TEXT NOT NULL CHECK (role IN ('athlete', 'coach', 'admin')),
    student_id    TEXT UNIQUE,                -- athletes only
    team_id       INTEGER REFERENCES teams (id),  -- athletes and coaches
    created_at    TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);

-- Week 4: add the study_sessions table below.
