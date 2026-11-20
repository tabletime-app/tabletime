from flask import g

from tabletime.times import local_time


def test_home_without_a_user_shows_the_welcome_page(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Acting as" in response.data


def test_acting_as_sets_the_user(client, act_as):
    act_as("coach@example.edu")
    with client:
        client.get("/coach/")
        assert g.user["email"] == "coach@example.edu"
        assert g.user["role"] == "coach"


def test_home_sends_each_role_to_its_page(client, act_as):
    for email, page, heading in [("athlete@example.edu", "/athlete/", b"My study hours"),
                                 ("coach@example.edu", "/coach/", b"Team hours"),
                                 ("admin@example.edu", "/admin/", b"Administration")]:
        act_as(email)
        response = client.get("/")
        assert response.headers["Location"] == page
        assert heading in client.get(page).data


def test_picking_nobody_clears_the_user(client, act_as):
    act_as("coach@example.edu")
    client.post("/dev/act-as", data={"user_id": ""})
    with client:
        client.get("/")
        assert g.user is None


def test_the_menu_can_be_turned_off(app, client, act_as):
    app.config["ACTING_AS_MENU"] = False
    assert client.post("/dev/act-as", data={"user_id": 1}).status_code == 404
    assert b"Acting as" not in client.get("/").data


def test_display_page_renders(client):
    assert client.get("/display").status_code == 200


def test_local_time_filter_shows_central_time(app):
    with app.app_context():
        # 23:05 UTC on Feb 15 is 5:05 pm in Central time (UTC-6 in February).
        assert local_time("2027-02-15T23:05:00Z", "%H:%M") == "17:05"
        # In July, Central time is UTC-5.
        assert local_time("2027-07-15T23:05:00Z", "%H:%M") == "18:05"
