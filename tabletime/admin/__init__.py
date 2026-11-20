"""Admin pages: teams, coach accounts, and the study table's open hours.

Owned by the group member who builds the admin pages. Templates go in
tabletime/admin/templates/admin/, and this part's tables go in
tabletime/admin/schema.sql.

To add fake rows for this part's tables (for example, open hours), define
seed(db) in this file. `flask --app tabletime seed` calls it after the shared
teams, users and study sessions exist:

    def seed(db):
        db.execute("INSERT INTO ...", (...))
"""
from flask import Blueprint, render_template

bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="templates")


@bp.route("/")
def home():
    return render_template("admin/home.html")
