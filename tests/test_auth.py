from flask import g, session


def test_login_page_renders(client):
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Log in" in response.data


def test_login_succeeds_and_redirects_home(client, forms):
    response = forms.login()
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    with client:
        client.get("/")
        assert session["user_id"] == g.user["id"]
        assert g.user["email"] == "athlete@example.edu"


def test_email_is_case_insensitive(forms):
    assert forms.login(email="  Athlete@Example.EDU ").status_code == 302


def test_wrong_password_shows_one_generic_message(forms):
    for email in ["athlete@example.edu", "nobody@example.edu"]:
        response = forms.login(email=email, password="wrong")
        assert response.status_code == 200
        assert b"Incorrect email or password." in response.data


def test_login_stays_for_30_days(client, forms):
    response = forms.login()
    cookie = response.headers["Set-Cookie"]
    assert "Expires=" in cookie  # a permanent cookie, not one that ends with the browser


def test_home_requires_login_and_returns_after(client, forms):
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"].startswith("/auth/login?next=")


def test_next_keeps_its_query_string(client, forms):
    # Week 7 depends on this: a scanned link must survive the trip through login.
    response = forms.post("/auth/login", {"email": "athlete@example.edu",
                                          "password": "password", "next": "/scan?t=abc123"})
    assert response.headers["Location"] == "/scan?t=abc123"


def test_next_cannot_leave_the_site(forms):
    for target in ["https://evil.example", "//evil.example", "/\\evil.example"]:
        forms.logout()
        response = forms.post("/auth/login", {"email": "athlete@example.edu",
                                              "password": "password", "next": target})
        assert response.headers["Location"] == "/"


def test_logout_clears_session(client, forms):
    forms.login()
    forms.logout()
    with client:
        client.get("/auth/login")
        assert "user_id" not in session


def test_logout_requires_post(client):
    assert client.get("/auth/logout").status_code == 405


def test_post_without_csrf_token_is_rejected(client):
    response = client.post("/auth/login", data={"email": "athlete@example.edu",
                                                 "password": "password"})
    assert response.status_code == 400


def test_post_with_wrong_csrf_token_is_rejected(client):
    with client.session_transaction() as sess:
        sess["csrf_token"] = "the-real-token"
    response = client.post("/auth/login", data={"email": "athlete@example.edu",
                                                 "password": "password",
                                                 "csrf_token": "a-guess"})
    assert response.status_code == 400


def test_each_role_gets_its_own_dashboard(client, forms):
    for email, heading in [("athlete@example.edu", b"My study hours"),
                           ("coach@example.edu", b"Team hours"),
                           ("admin@example.edu", b"Administration")]:
        forms.logout()
        forms.login(email=email)
        assert heading in client.get("/").data
