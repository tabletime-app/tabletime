"""Admin pages: teams, coach accounts, and the study table's open hours.

Owned by the group member who builds the admin pages. Templates go in
tabletime/admin/templates/admin/, and this part's tables go in
tabletime/admin/schema.sql.
"""
from flask import Blueprint, render_template

bp = Blueprint("admin", __name__, url_prefix="/admin", template_folder="templates")


@bp.route("/")
def home():
    return render_template("admin/home.html")
