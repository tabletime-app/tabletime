"""TableTime: track study table hours for student athletes.

This file holds the application factory. Flask calls create_app() to build
the app; tests call it too, with their own settings.
"""
import os

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        # "dev" is fine on your laptop. Anywhere else, set a long random value
        # in the TABLETIME_SECRET_KEY environment variable.
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path, "tabletime.sqlite"),
        # Times are stored in UTC and shown in this time zone.
        TIMEZONE="America/Chicago",
        # How long a QR code stays valid, and how often the display page
        # should fetch a new one. See tabletime/tokens.py.
        QR_TOKEN_SECONDS=30,
        QR_REFRESH_SECONDS=15,
        # The "Acting as" menu in the page header. It stands in for logging
        # in until the shared login is added, and that change turns it off.
        ACTING_AS_MENU=True,
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
        app.config.from_prefixed_env("TABLETIME")
    else:
        app.config.from_mapping(test_config)

    os.makedirs(app.instance_path, exist_ok=True)

    from . import db, dev, main
    from .admin import bp as admin_bp
    from .athlete import bp as athlete_bp
    from .coach import bp as coach_bp
    from .scan import bp as scan_bp

    db.init_app(app)
    app.register_blueprint(dev.bp)
    app.register_blueprint(main.bp)

    # One blueprint for each part of the app. Each part's routes, templates
    # and tables live in its own folder, so group members rarely edit the
    # same files.
    app.register_blueprint(scan_bp)
    app.register_blueprint(athlete_bp)
    app.register_blueprint(coach_bp)
    app.register_blueprint(admin_bp)

    from .times import local_time
    app.jinja_env.filters["local_time"] = local_time

    return app
