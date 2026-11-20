"""TableTime: track study table hours for student athletes.

This file holds the application factory. Flask calls create_app() to build
the app; tests call it too, with their own settings.
"""
import os
from datetime import timedelta

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        # "dev" is fine on your laptop. Anywhere else, set a long random value
        # in the TABLETIME_SECRET_KEY environment variable.
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "tabletime.sqlite"),
        # Logged-in users stay logged in for 30 days, so athletes don't have
        # to sign in again every time they scan a code.
        PERMANENT_SESSION_LIFETIME=timedelta(days=30),
        # Times are stored in UTC and shown in this time zone.
        TIMEZONE="America/Chicago",
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
        app.config.from_prefixed_env("TABLETIME")
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    from . import auth, db, main, security

    db.init_app(app)
    security.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)

    return app
