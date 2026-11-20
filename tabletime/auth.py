"""Logging in and out, and the login_required decorator."""
import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.before_app_request
def load_logged_in_user():
    """Before every request, look up the logged-in user (or None) and store it on g."""
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def login_required(view):
    """Send visitors who aren't logged in to the login page, then back here."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))
        return view(**kwargs)
    return wrapped_view


# Week 3: write role_required(*roles) here. See tests/test_week03_roles.py.


def safe_next(target):
    """Return target only if it is a path on this site.

    Without this check, a link like /auth/login?next=https://evil.example
    would send users to another site after they log in (an "open redirect").
    """
    if target and target.startswith("/") and not target.startswith("//") and "\\" not in target:
        return target
    return None


@bp.route("/login", methods=("GET", "POST"))
def login():
    next_url = request.values.get("next")
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            # Same message either way, so the form doesn't reveal which emails exist.
            flash("Incorrect email or password.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            session.permanent = True  # keep the login for PERMANENT_SESSION_LIFETIME
            return redirect(safe_next(next_url) or url_for("main.index"))

    return render_template("auth/login.html", next_url=next_url)


@bp.route("/logout", methods=("POST",))
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


# Week 2: add the /auth/register route here. See tests/test_week02_register.py.
