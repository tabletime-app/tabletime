# TableTime

TableTime tracks study table hours for student athletes. Athletes clock in
and out by scanning a QR code shown on a screen at the study table, coaches
see which athletes met their team's weekly minimum, and admins manage teams
and the study table's open hours.

It is built with Flask, SQLite, and plain HTML, CSS, and JavaScript. It is
also the class project for CS 253 at Illinois Wesleyan University, where
each project group builds the app from this starting code. The `main` branch
is that starting code: the structure, the shared tables, fake data, and a
helper for signed QR codes, with the features themselves left to build.

## Get it running

You need Python 3.10 or newer.

```bash
python3 -m venv venv
source venv/bin/activate
# In Git Bash on Windows, use these two lines instead:
#   python -m venv venv
#   source venv/Scripts/activate
pip install -r requirements.txt

flask --app tabletime init-db     # create empty tables
flask --app tabletime seed        # add fake teams, coaches, athletes and study sessions
flask --app tabletime run --debug
```

Open http://127.0.0.1:5000. There is no login page yet. Instead, pick a user
from the **Acting as** menu at the top of the page, and TableTime treats you
as that user. The seed adds an admin, a coach and 8 athletes for each of four
teams, and about ten weeks of study sessions, so every page has data to show.

## Run the tests

```bash
pytest
```

Every test must pass before a pull request is merged. Add tests for each
route you write, including at least one test of something that should be
refused. Put your part's tests in a file of its own, `tests/test_<part>.py`
(for example `tests/test_coach.py`). Don't add them to `tests/test_pages.py`:
that file belongs to the shared code, and the shared login rewrites it.

Tests that depend on the time of day or the day of the week should fix the
clock with the `freeze_time` fixture from `tests/conftest.py`:

```python
from datetime import datetime, timezone

def test_this_weeks_total(client, act_as, freeze_time):
    freeze_time(datetime(2027, 2, 17, 18, 0, tzinfo=timezone.utc))
    ...
```

It replaces `tabletime.times.utc_now()`, so code that gets the time from
`times.utc_now()`, `times.now_text()` or `times.week_bounds()` sees that
moment. QR tokens read the system clock instead, so pass them the time:
`make_token(now=moment.timestamp())` and `check_token(token, now=...)`.

## How the code is organized

The app has four parts, and each has its own folder with its routes
(a Flask blueprint), its templates and its tables:

| Folder | Part | What it covers |
| --- | --- | --- |
| `tabletime/scan/` | Display and scan | The QR display page, the scan route, clocking in and out |
| `tabletime/athlete/` | Athlete pages | An athlete's history and progress toward this week's minimum |
| `tabletime/coach/` | Coach pages | The roster against the minimum, setting minimums, corrections with an audit trail |
| `tabletime/admin/` | Admin pages | Teams, coach accounts, open hours |

Each part's tables go in its own `schema.sql`. To add fake rows to a part's
tables (open hours, team minimums), define a `seed(db)` function in that
part's `__init__.py`; `flask --app tabletime seed` calls it after the shared
teams, users and study sessions exist. Shared code that every part uses is at
the top level:

| Path | What it does |
| --- | --- |
| `tabletime/__init__.py` | Application factory and settings |
| `tabletime/schema.sql` | The shared tables: `teams`, `users`, `study_sessions` |
| `tabletime/db.py` | Database connection; the `init-db` and `seed` commands |
| `tabletime/dev.py` | The development-only "Acting as" menu, which sets `g.user` |
| `tabletime/tokens.py` | Signed QR tokens with an expiry: `make_token()` and `check_token()` |
| `tabletime/times.py` | The current time (`utc_now()`), week boundaries, form values, and local time on the page |
| `tabletime/templates/` | The page layout and the welcome page |
| `tabletime/static/style.css` | Mobile-first styles |
| `tests/` | Tests for the shared code |

Changes to the shared files affect everyone, so they go through a pull
request that the whole group agrees on.

### The current user

Your routes read the current user from `g.user` (a row from `users`, or
`None`): `g.user["id"]`, `g.user["role"]`, `g.user["team_id"]`. For now the
"Acting as" menu sets it. When logins are added, a login sets it instead and
the menu goes away, so code that reads `g.user` keeps working.

### Times

Every time in the database is UTC text such as `2027-02-15T23:05:00Z`.
`tabletime/times.py` has what the parts need:

- `times.utc_now()` and `times.now_text()`: the current time. Get it only
  from here, so tests can fix the clock.
- `times.week_bounds()`: this study week, Monday 00:00 to the next Monday in
  local time, as two UTC texts for `clock_in >= ? AND clock_in < ?`.
- `times.minutes_between(start, end)`: the length of a session in minutes.
- `times.from_form(value)` and the `to_form` filter: convert between UTC
  text and an `<input type="datetime-local">` value, which is local time.
- The `local_time` filter shows a time on a page: `{{ s["clock_in"] | local_time }}`.

Import the module (`from .. import times`) and call `times.utc_now()`, so the
test clock can replace it.

## Settings

Put settings in `instance/config.py` (not committed), or in environment
variables that start with `TABLETIME_`. Before running anywhere other than
your own laptop, set a long random secret key, since it signs the QR codes:

```bash
export TABLETIME_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
