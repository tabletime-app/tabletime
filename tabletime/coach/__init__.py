"""Coach pages: the team roster against the weekly minimum, and corrections.

Owned by the group member who builds the coach pages. Templates go in
tabletime/coach/templates/coach/, and this part's tables go in
tabletime/coach/schema.sql.

To add fake rows for this part's tables (for example, team minimums), define
seed(db) in this file. `flask --app tabletime seed` calls it after the shared
teams, users and study sessions exist:

    def seed(db):
        db.execute("INSERT INTO ...", (...))
"""
from flask import Blueprint, render_template

bp = Blueprint("coach", __name__, url_prefix="/coach", template_folder="templates")


@bp.route("/")
def home():
    return render_template("coach/home.html")
