"""Display and scan: the QR code at the study table, and clocking in and out.

Owned by the group member who builds the display page and the scan route.
Templates go in tabletime/scan/templates/scan/, and this part's tables go in
tabletime/scan/schema.sql.

Start from tabletime/tokens.py: make_token() for the code on the display page,
check_token() in the scan route. The QR code itself can be drawn as SVG with
the qrcode package (qrcode.image.svg), so no image library is needed.

To add fake rows for this part's tables, define
seed(db) in this file. `flask --app tabletime seed` calls it after the shared
teams, users and study sessions exist:

    def seed(db):
        db.execute("INSERT INTO ...", (...))
"""
from flask import Blueprint, render_template

bp = Blueprint("scan", __name__, template_folder="templates")


@bp.route("/display")
def display():
    """The page shown on the screen at the study table (admins only, once logins exist)."""
    return render_template("scan/display.html")


# The scan route goes here. The QR code holds a URL such as
# http://<server>/scan?t=<token>, which opens on the athlete's phone.
