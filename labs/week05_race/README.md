# Week 5 lab: why we use a database

Thirty athletes walk into study tables and scan the code within the same few
seconds. This lab saves their check-ins two ways and counts what survives.

```bash
python labs/week05_race/race.py
```

## Part 1: run it

Run the script three times. For each store, record how many of the 30 new
check-ins were saved and whether the earlier history survived.

## Part 2: explain it

1. `JsonStore.append` reads the file, adds one record, and writes the file back.
   Draw a timeline for two athletes, A and B, that ends with A's check-in missing.
2. Some runs lose the earlier history too. `save` opens the file with `"w"`.
   What does another thread see if it calls `load` at that moment, and what
   does `load` return? Follow that value through `append`.
3. Why does SQLite keep every check-in, even though 30 threads write at once?
   Look up what SQLite does while one connection is writing.

## Part 3: try a fix

Add a `threading.Lock` to `JsonStore` so that `append` holds it from `load`
to `save`. Run the script again.

1. Did it fix the problem?
2. Real Flask deployments often run several worker *processes*. Would your
   lock still work across processes? Why or why not?
3. Name one more thing a database gives you that the JSON file doesn't.

## Part 4: back to TableTime

An athlete must not have two open study sessions at once. Add a partial
unique index to `study_sessions` that enforces this in the database:

```sql
CREATE UNIQUE INDEX one_open_session
    ON study_sessions (user_id) WHERE clock_out IS NULL;
```

Write a test that clocks the same athlete in twice and checks that the second
attempt is refused. Then explain why checking "does this athlete already have
an open session?" in Python, before the INSERT, is not enough on its own.
