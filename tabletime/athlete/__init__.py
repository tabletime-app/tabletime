"""Athlete pages: an athlete's own history and progress toward this week's minimum.

Owned by the group member who builds the athlete pages. Templates go in
tabletime/athlete/templates/athlete/, and this part's tables go in
tabletime/athlete/schema.sql.
"""
from flask import Blueprint, render_template

bp = Blueprint("athlete", __name__, url_prefix="/athlete", template_folder="templates")


@bp.route("/")
def home():
    return render_template("athlete/home.html")
