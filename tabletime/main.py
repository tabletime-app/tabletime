"""Pages that aren't about logging in."""
from flask import Blueprint, g, render_template

from .auth import login_required

bp = Blueprint("main", __name__)

DASHBOARDS = {
    "athlete": "dashboards/athlete.html",
    "coach": "dashboards/coach.html",
    "admin": "dashboards/admin.html",
}


@bp.route("/")
@login_required
def index():
    """Each role lands on its own dashboard. Weeks 9 to 12 fill these in."""
    return render_template(DASHBOARDS[g.user["role"]])
