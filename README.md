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
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
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
refused.

## How the code is organized

The app has four parts, and each has its own folder with its routes
(a Flask blueprint), its templates and its tables:

| Folder | Part | What it covers |
| --- | --- | --- |
| `tabletime/scan/` | Display and scan | The QR display page, the scan route, clocking in and out |
| `tabletime/athlete/` | Athlete pages | An athlete's history and progress toward this week's minimum |
| `tabletime/coach/` | Coach pages | The roster against the minimum, setting minimums, corrections with an audit trail |
| `tabletime/admin/` | Admin pages | Teams, coach accounts, open hours |

Each part's tables go in its own `schema.sql`. Shared code that every part
uses is at the top level:

| Path | What it does |
| --- | --- |
| `tabletime/__init__.py` | Application factory and settings |
| `tabletime/schema.sql` | The shared tables: `teams`, `users`, `study_sessions` |
| `tabletime/db.py` | Database connection; the `init-db` and `seed` commands |
| `tabletime/dev.py` | The development-only "Acting as" menu, which sets `g.user` |
| `tabletime/tokens.py` | Signed QR tokens with an expiry: `make_token()` and `check_token()` |
| `tabletime/times.py` | UTC text in the database, local time on the page |
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

Every time in the database is UTC text such as `2027-02-15T23:05:00Z`. Use
`times.now_text()` to store the current time, and the `local_time` filter to
show a time on a page: `{{ s["clock_in"] | local_time }}`.

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
