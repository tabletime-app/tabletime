"""Protection against cross-site request forgery (CSRF).

Another website could contain a hidden form that posts to this app. The
browser would send the user's session cookie along with it, so the app would
think the user submitted it. To stop that, every form includes a secret token
that only pages from this app know, and every POST must send it back.

In a template:  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
"""
import secrets

from flask import abort, request, session


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def check_csrf():
    if request.method != "POST":
        return
    expected = session.get("csrf_token")
    sent = request.form.get("csrf_token", "")
    if not expected or not secrets.compare_digest(sent, expected):
        abort(400, "This form expired or was not sent from this site. Reload the page and try again.")


def init_app(app):
    app.jinja_env.globals["csrf_token"] = csrf_token
    app.before_request(check_csrf)
