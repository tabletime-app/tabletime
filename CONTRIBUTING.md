# Contributing

## How we work

1. Make a branch for each change: `git switch -c week02-register`.
2. Commit in small steps with messages that say what changed and why.
3. Run `pytest` before you push. Every test must pass or be skipped.
4. Open a pull request. At least one teammate reviews it before it merges.
5. Never commit the `instance/` folder, a database file, or a secret key.

## Code style

- Follow the patterns already in the starter: blueprints for groups of pages,
  `get_db()` for database access, `?` placeholders in every SQL query.
- Never build SQL by putting user input into a string. Use placeholders.
- Every form that posts includes the CSRF token (see `tabletime/security.py`).
- Write a test for each feature, including at least one test of something
  that should be refused.

## Licensing

By contributing, you agree that your contribution is released under the
project's MIT license.
