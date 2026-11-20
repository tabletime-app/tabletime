"""The "Acting as" menu: a stand-in for logging in, for development only.

Until the class reaches logins, TableTime has no login page. Instead, the
header has a menu of the seeded users, and the app treats whoever you pick
as the logged-in user. Your code reads that user from g.user, exactly as it
will once real logins exist:

    g.user["id"], g.user["role"], g.user["team_id"]

g.user is None when nobody is picked.

This menu is the opposite of security: anyone can claim to be anyone. That is
fine on your own laptop and nowhere else. The shared login change removes it,
and your routes keep working because they already read g.user.
"""
from flask import Blueprint, current_app, g, redirect, request, session, url_for

from .db import get_db

bp = Blueprint("dev", __name__, url_prefix="/dev")


def menu_enabled():
    return current_app.config.get("ACTING_AS_MENU", False)


@bp.before_app_request
def load_acting_user():
    g.user = None
    if not menu_enabled():
        return
    user_id = session.get("acting_as")
    if user_id is not None:
        g.user = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


@bp.app_context_processor
def acting_as_choices():
    """Give base.html the list of users for the menu."""
    if not menu_enabled():
        return {"acting_as_users": []}
    users = get_db().execute(
        "SELECT users.id, users.name, users.role, teams.name AS team"
        " FROM users LEFT JOIN teams ON teams.id = users.team_id"
        " ORDER BY CASE users.role WHEN 'admin' THEN 0 WHEN 'coach' THEN 1 ELSE 2 END,"
        " teams.name, users.name").fetchall()
    return {"acting_as_users": users}


@bp.route("/act-as", methods=("POST",))
def act_as():
    if not menu_enabled():
        return "The Acting as menu is turned off.", 404
    user_id = request.form.get("user_id", type=int)
    if user_id is None:
        session.pop("acting_as", None)
    else:
        session["acting_as"] = user_id
    return redirect(url_for("main.index"))
