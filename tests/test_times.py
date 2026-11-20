from datetime import datetime, timezone

from tabletime import times


def utc(*args):
    return datetime(*args, tzinfo=timezone.utc)


def test_week_runs_monday_to_monday_in_central_time(app):
    with app.app_context():
        # Wed Feb 17, 2027, 3 am UTC is still Tuesday evening in Central time.
        start, end = times.week_bounds(utc(2027, 2, 17, 3, 0))
    # Monday Feb 15 at midnight Central (UTC-6) is 6 am UTC.
    assert (start, end) == ("2027-02-15T06:00:00Z", "2027-02-22T06:00:00Z")


def test_a_sunday_night_belongs_to_the_week_before(app):
    with app.app_context():
        # Sun Feb 21, 11:30 pm Central is Mon Feb 22, 5:30 am UTC.
        start, _ = times.week_bounds(utc(2027, 2, 22, 5, 30))
    assert start == "2027-02-15T06:00:00Z"


def test_week_containing_the_change_to_daylight_saving_time(app):
    with app.app_context():
        # Clocks change on Sun Mar 14, 2027. The week starts in standard time
        # (UTC-6) and ends in daylight time (UTC-5), so it is 167 hours long.
        start, end = times.week_bounds(utc(2027, 3, 10, 18, 0))
        assert (start, end) == ("2027-03-08T06:00:00Z", "2027-03-15T05:00:00Z")
        assert times.minutes_between(start, end) == 167 * 60


def test_week_bounds_uses_the_test_clock(app, freeze_time):
    freeze_time(utc(2027, 2, 17, 18, 0))
    with app.app_context():
        assert times.week_bounds() == ("2027-02-15T06:00:00Z", "2027-02-22T06:00:00Z")
        assert times.now_text() == "2027-02-17T18:00:00Z"


def test_minutes_between():
    assert times.minutes_between("2027-02-15T23:00:00Z", "2027-02-16T00:30:00Z") == 90


def test_form_values_are_local_time(app):
    with app.app_context():
        # A datetime-local field holds local time with no zone.
        assert times.from_form("2027-02-15T18:30") == "2027-02-16T00:30:00Z"
        assert times.to_form("2027-02-16T00:30:00Z") == "2027-02-15T18:30"
        assert times.to_form(None) == ""


def test_to_form_filter_is_available_in_templates(app):
    with app.app_context():
        template = app.jinja_env.from_string('{{ "2027-07-15T23:05:00Z" | to_form }}')
        assert template.render() == "2027-07-15T18:05"
