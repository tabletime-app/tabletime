"""Week 2 acceptance tests: athlete self-registration.

Delete the `pytestmark` line below when you start this feature. These tests
define the form: field names, where it posts, and what it must reject.
Add tests of your own for anything else your version does.
"""
import pytest

from tabletime.db import get_db

pytestmark = pytest.mark.skip(reason="Week 2: delete this line when you start registration")

GOOD = {
    "name": "Robin Runner",
    "email": "Robin@Example.edu",
    "student_id": "1000099",
    "team_id": "1",
    "password": "correct-horse-battery",
}


def user_with_email(app, email):
    with app.app_context():
        return get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()


def test_register_page_lists_teams(client):
    response = client.get("/auth/register")
    assert response.status_code == 200
    assert b"Soccer" in response.data and b"Swimming" in response.data


def test_register_creates_athlete_and_redirects_to_login(app, forms):
    response = forms.post("/auth/register", GOOD)
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/auth/login")

    user = user_with_email(app, "robin@example.edu")  # stored lowercase
    assert user["role"] == "athlete"
    assert user["team_id"] == 1
    assert user["password_hash"] != GOOD["password"]


def test_new_athlete_can_log_in(forms):
    forms.post("/auth/register", GOOD)
    assert forms.login(email="robin@example.edu", password=GOOD["password"]).status_code == 302


@pytest.mark.parametrize("field", ["name", "email", "student_id", "team_id", "password"])
def test_every_field_is_required(app, forms, field):
    response = forms.post("/auth/register", {**GOOD, field: ""})
    assert response.status_code == 200  # form shown again, with a message
    assert user_with_email(app, "robin@example.edu") is None


def test_short_password_is_rejected(app, forms):
    response = forms.post("/auth/register", {**GOOD, "password": "short"})
    assert response.status_code == 200
    assert user_with_email(app, "robin@example.edu") is None


def test_duplicate_email_is_rejected(app, forms):
    response = forms.post("/auth/register", {**GOOD, "email": "ATHLETE@example.edu"})
    assert response.status_code == 200
    assert b"already" in response.data.lower()


def test_duplicate_student_id_is_rejected(app, forms):
    response = forms.post("/auth/register", {**GOOD, "student_id": "1000001"})
    assert response.status_code == 200
    assert user_with_email(app, "robin@example.edu") is None


def test_unknown_team_is_rejected(app, forms):
    response = forms.post("/auth/register", {**GOOD, "team_id": "999"})
    assert response.status_code == 200
    assert user_with_email(app, "robin@example.edu") is None


def test_cannot_register_as_admin(app, forms):
    forms.post("/auth/register", {**GOOD, "role": "admin"})
    assert user_with_email(app, "robin@example.edu")["role"] == "athlete"
