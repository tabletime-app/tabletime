"""Signed QR tokens: the text inside each QR code on the display page.

A token holds two things: a random code and the time it was made. The app
signs both with its secret key (an HMAC, using itsdangerous), so nobody can
make a token or change its time without the key. Because the time is inside
the signed part, an old screenshot can't be made to look new.

What this module does NOT do is stop a token from being used twice. A valid
token stays valid for QR_TOKEN_SECONDS, and two athletes standing at the table
can both scan it. Stopping the same athlete from using the same code twice,
and refusing scans outside open hours, are the scan route's job, and the
database is the right place to enforce the first (a UNIQUE constraint).

Typical use in the scan part of the app:

    token = make_token()                      # display page: put this in the QR code
    code = check_token(request.args["t"])     # scan route: raises BadToken if invalid
"""
import secrets
import time

from flask import current_app
from itsdangerous import BadSignature, URLSafeSerializer


class BadToken(Exception):
    """The token was changed, made without the key, or has expired."""


def _serializer():
    return URLSafeSerializer(current_app.config["SECRET_KEY"], salt="qr-token")


def make_token(now=None):
    """Return a new signed token as a short string that is safe to put in a URL."""
    issued = int(time.time() if now is None else now)
    return _serializer().dumps({"code": secrets.token_urlsafe(8), "issued": issued})


def check_token(token, now=None, max_age=None):
    """Check a token and return its random code.

    Raises BadToken if the signature doesn't match, or if the token is older
    than max_age seconds (QR_TOKEN_SECONDS by default) or dated in the future.
    The returned code identifies the token, so the scan route can record
    which athlete used which code.
    """
    if max_age is None:
        max_age = current_app.config["QR_TOKEN_SECONDS"]
    now = int(time.time() if now is None else now)
    try:
        data = _serializer().loads(token)
    except BadSignature as e:
        raise BadToken("This code wasn't made by TableTime.") from e

    age = now - data["issued"]
    if age > max_age:
        raise BadToken("This code has expired. Scan the code on the screen again.")
    if age < -5:  # a few seconds of clock difference is fine; more is not
        raise BadToken("This code is dated in the future.")
    return data["code"]
