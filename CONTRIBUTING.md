# Contributing

## How we work

1. Work on an issue, and make a branch for it: `git switch -c coach-roster`.
2. Commit in small steps with messages that say what changed and why.
3. Run `pytest` before you push. Every test must pass.
4. Open a pull request. Another group member reviews and approves it before it
   merges, and GitHub Actions must show the tests passing.
5. Never commit the `instance/` folder, a database file, or a secret key.

## Your part of the app

Work inside your part's folder (`tabletime/scan/`, `athlete/`, `coach/` or
`admin/`): its routes, its templates and its `schema.sql`. Changes to the
shared files (`tabletime/__init__.py`, `schema.sql`, `db.py`, `dev.py`,
`tokens.py`, `times.py`, `templates/base.html`, `static/style.css`) affect
everyone, so they go in a pull request of their own that the whole group
agrees on.

## Updates from the class repository

Your group's repository is a copy of a class repository, and a remote named
`upstream` points at it. When the instructor adds something to the class
repository, bring it into yours on a branch and open a pull request, the same
as any other change. (Branch protection on `main` refuses a direct push, even
of a merge.)

```bash
git switch main
git pull                          # start from your group's latest main
git fetch upstream                # download the class repository's commits
git switch -c merge-upstream      # a branch for the merge
git merge upstream/main           # resolve any conflicts, then commit
pytest
git push -u origin merge-upstream
```

Then open a pull request from `merge-upstream`, and have another member review
and approve it. Once it is merged, each member runs `git switch main` and
`git pull`, then `git merge main` on each branch they are still working on.

If `git remote -v` doesn't list `upstream`, add it once with
`git remote add upstream <the class repository's address>`.

## Code style

- Follow the patterns already here: a blueprint for each part, `get_db()` for
  database access, and `?` placeholders in every SQL query.
- Never build SQL by putting user input into a string. Use placeholders.
- Read the current user from `g.user`, never from a form field or the URL.
- Store times as UTC text (`times.now_text()`), and show them with the
  `local_time` filter.
- Write a test for each feature, including at least one test of something
  that should be refused.

## Licensing

By contributing, you agree that your contribution is released under the
project's MIT license.
