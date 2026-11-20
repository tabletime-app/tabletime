import pytest

from tabletime.tokens import BadToken, check_token, make_token

NOW = 1_800_000_000  # a fixed time, so the tests don't depend on the clock


def test_a_fresh_token_is_accepted(app):
    with app.app_context():
        token = make_token(now=NOW)
        assert check_token(token, now=NOW + 10)


def test_each_token_has_its_own_code(app):
    with app.app_context():
        codes = {check_token(make_token(now=NOW), now=NOW) for _ in range(20)}
    assert len(codes) == 20


def test_an_expired_token_is_refused(app):
    with app.app_context():
        token = make_token(now=NOW)
        seconds = app.config["QR_TOKEN_SECONDS"]
        assert check_token(token, now=NOW + seconds)
        with pytest.raises(BadToken, match="expired"):
            check_token(token, now=NOW + seconds + 1)


def test_a_token_from_the_future_is_refused(app):
    with app.app_context():
        with pytest.raises(BadToken):
            check_token(make_token(now=NOW + 60), now=NOW)


def test_a_changed_token_is_refused(app):
    with app.app_context():
        token = make_token(now=NOW)
        changed = token[:-1] + ("A" if token[-1] != "A" else "B")
        with pytest.raises(BadToken):
            check_token(changed, now=NOW)


def test_a_token_signed_with_another_key_is_refused(app):
    with app.app_context():
        app.config["SECRET_KEY"] = "another key"
        token = make_token(now=NOW)
        app.config["SECRET_KEY"] = "test"
        with pytest.raises(BadToken):
            check_token(token, now=NOW)


def test_the_time_is_covered_by_the_signature(app):
    # Rebuilding an old token with a newer time, without the key, must fail.
    from itsdangerous import URLSafeSerializer
    with app.app_context():
        forged = URLSafeSerializer("a guess", salt="qr-token").dumps(
            {"code": "abc", "issued": NOW})
        with pytest.raises(BadToken):
            check_token(forged, now=NOW)
