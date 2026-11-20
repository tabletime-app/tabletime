"""Week 5 lab: 30 athletes check in at the same moment. How many are saved?

Run it:   python labs/week05_race/race.py
Options:  --athletes 30  --history 5000  --trials 5

Each simulated athlete runs in its own thread, like requests in a web server.
The same check-ins go to two stores:
  1. JsonStore: read the whole JSON file, add one record, write it all back.
  2. SQLite: one INSERT per check-in, each thread with its own connection.
"""
import argparse
import json
import os
import sqlite3
import tempfile
import threading
from datetime import datetime, timezone

from json_store import JsonStore


def checkin(athlete_number):
    return {"athlete": f"athlete{athlete_number}",
            "time": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}


def old_record(i):
    return {"athlete": f"old{i}", "time": "2026-09-01T18:00:00Z"}


def run_json(n_athletes, history):
    folder = tempfile.mkdtemp()
    path = os.path.join(folder, "checkins.json")
    JsonStore(path).save([old_record(i) for i in range(history)])

    start = threading.Barrier(n_athletes)

    def athlete(i):
        store = JsonStore(path)
        start.wait()  # everyone scans at the same instant
        store.load()  # the page looks up the athlete's last check-in first
        store.append(checkin(i))

    run_threads(athlete, n_athletes)
    try:
        with open(path) as f:
            records = json.load(f)
    except json.JSONDecodeError:
        return 0, 0, True
    new = sum(r["athlete"].startswith("athlete") for r in records)
    kept = sum(r["athlete"].startswith("old") for r in records)
    return new, kept, False


def run_sqlite(n_athletes, history):
    folder = tempfile.mkdtemp()
    path = os.path.join(folder, "checkins.sqlite")
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE checkins (id INTEGER PRIMARY KEY, athlete TEXT, time TEXT)")
        db.executemany("INSERT INTO checkins (athlete, time) VALUES (:athlete, :time)",
                       [old_record(i) for i in range(history)])

    start = threading.Barrier(n_athletes)

    def athlete(i):
        db = sqlite3.connect(path, timeout=10)
        start.wait()
        db.execute("SELECT * FROM checkins WHERE athlete = ? ORDER BY id DESC LIMIT 1",
                   (f"athlete{i}",)).fetchone()
        db.execute("INSERT INTO checkins (athlete, time) VALUES (:athlete, :time)", checkin(i))
        db.commit()
        db.close()

    run_threads(athlete, n_athletes)
    db = sqlite3.connect(path)
    new = db.execute("SELECT COUNT(*) FROM checkins WHERE athlete LIKE 'athlete%'").fetchone()[0]
    kept = db.execute("SELECT COUNT(*) FROM checkins WHERE athlete LIKE 'old%'").fetchone()[0]
    db.close()
    return new, kept, False


def run_threads(target, n):
    threads = [threading.Thread(target=target, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--athletes", type=int, default=30)
    parser.add_argument("--history", type=int, default=5000,
                        help="check-ins already saved before the rush")
    parser.add_argument("--trials", type=int, default=5)
    args = parser.parse_args()

    print(f"{args.athletes} athletes check in at once; {args.history} earlier check-ins on file.\n")
    print(f"{'store':<8}{'trial':>6}{'new saved':>12}{'history kept':>15}  note")
    for name, run in [("json", run_json), ("sqlite", run_sqlite)]:
        for trial in range(1, args.trials + 1):
            new, kept, corrupted = run(args.athletes, args.history)
            note = "file corrupted" if corrupted else ""
            if not corrupted and kept < args.history:
                note = "history lost"
            print(f"{name:<8}{trial:>6}{new:>7} / {args.athletes:<3}{kept:>9} / {args.history:<6} {note}")


if __name__ == "__main__":
    main()
