"""The home page, which sends each user to the home page for their role."""
from flask import Blueprint, g, redirect, render_template, url_for

bp = Blueprint("main", __name__)

HOMES = {"athlete": "athlete.home", "coach": "coach.home", "admin": "admin.home"}


@bp.route("/")
def index():
    if g.user is None:
        return render_template("welcome.html")
    return redirect(url_for(HOMES[g.user["role"]]))
