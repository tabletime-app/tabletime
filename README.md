# TableTime

TableTime tracks study table hours for student athletes. Athletes clock in
and out by scanning a QR code that changes every few seconds, coaches see who
met the team's weekly minimum, and admins manage teams, schedules, and reports.

It is built with Flask, SQLite, and plain HTML, CSS, and JavaScript, and it
doubles as the semester project for CS 253. The `main` branch is the starter
code; students build the features week by week.

## Get it running

You need Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

flask --app tabletime init-db     # create an empty database
flask --app tabletime seed        # add fake teams, coaches, and athletes
flask --app tabletime run --debug
```

Open http://127.0.0.1:5000 and log in as `admin@example.edu`, `coach1@example.edu`,
or `athlete11@example.edu`. Every seeded password is `password`.

To make a real admin account: `flask --app tabletime create-admin you@example.edu`

## Run the tests

```bash
pytest
```

Tests for features you haven't built yet are skipped. Each skipped file names
its week, for example `tests/test_week02_register.py`. Delete its `pytestmark`
line when you start that feature, and the tests tell you what's left.

## What's in the starter

| Path | What it does |
| --- | --- |
| `tabletime/__init__.py` | Application factory and settings |
| `tabletime/db.py` | Database connection; `init-db`, `seed`, and `create-admin` commands |
| `tabletime/schema.sql` | Tables for teams and users |
| `tabletime/auth.py` | Log in, log out, `login_required` |
| `tabletime/security.py` | CSRF protection for every form |
| `tabletime/main.py` | Sends each role to its dashboard |
| `tabletime/templates/` | Page layout, login form, placeholder dashboards |
| `tabletime/static/style.css` | Mobile-first styles |
| `labs/week05_race/` | The week 5 lab on race conditions |
| `tests/` | Tests for the starter, plus skipped tests for weeks 2 and 3 |

Comments that start with `Week N:` mark where that week's work goes.

## Settings

Put settings in `instance/config.py` (not committed), or in environment
variables that start with `TABLETIME_`. Before running anywhere other than
your own laptop, set a long random secret key:

```bash
export TABLETIME_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
