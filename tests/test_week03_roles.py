"""Week 3 acceptance tests: roles, and admin pages for teams and coaches.

Delete the `pytestmark` line below when you start this feature.
"""
import pytest

from tabletime.db import get_db

pytestmark = pytest.mark.skip(reason="Week 3: delete this line when you start roles")

ADMIN_PAGES = ["/admin/teams", "/admin/coaches"]


def test_role_required_allows_listed_roles_only(app, client, forms):
    from tabletime.auth import role_required

    @app.route("/test-coaches-only")
    @role_required("coach", "admin")
    def coaches_only():
        return "ok"

    forms.login(email="coach@example.edu")
    assert client.get("/test-coaches-only").status_code == 200
    forms.logout()
    forms.login(email="athlete@example.edu")
    assert client.get("/test-coaches-only").status_code == 403


@pytest.mark.parametrize("page", ADMIN_PAGES)
def test_admin_pages_send_visitors_to_login(client, page):
    response = client.get(page)
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/auth/login")


@pytest.mark.parametrize("page", ADMIN_PAGES)
@pytest.mark.parametrize("email", ["athlete@example.edu", "coach@example.edu"])
def test_admin_pages_forbid_other_roles(client, forms, page, email):
    forms.login(email=email)
    assert client.get(page).status_code == 403


@pytest.mark.parametrize("email", ["athlete@example.edu", "coach@example.edu"])
def test_other_roles_cannot_post_to_admin_pages(app, forms, email):
    forms.login(email=email)
    response = forms.post("/admin/teams", {"name": "Tennis"})
    assert response.status_code == 403
    with app.app_context():
        assert get_db().execute("SELECT * FROM teams WHERE name = 'Tennis'").fetchone() is None


def test_admin_creates_team(app, client, forms):
    forms.login(email="admin@example.edu")
    forms.post("/admin/teams", {"name": "Tennis"})
    with app.app_context():
        assert get_db().execute("SELECT * FROM teams WHERE name = 'Tennis'").fetchone()
    assert b"Tennis" in client.get("/admin/teams").data


def test_duplicate_team_name_is_rejected(app, forms):
    forms.login(email="admin@example.edu")
    response = forms.post("/admin/teams", {"name": "Soccer"})
    assert response.status_code == 200
    with app.app_context():
        count = get_db().execute("SELECT COUNT(*) FROM teams WHERE name = 'Soccer'").fetchone()[0]
        assert count == 1


def test_admin_creates_coach_for_a_team(app, forms):
    forms.login(email="admin@example.edu")
    forms.post("/admin/coaches", {"name": "Pat Coach", "email": "pat@example.edu",
                                  "password": "a-long-password", "team_id": "2"})
    with app.app_context():
        coach = get_db().execute(
            "SELECT * FROM users WHERE email = 'pat@example.edu'").fetchone()
    assert coach["role"] == "coach"
    assert coach["team_id"] == 2
