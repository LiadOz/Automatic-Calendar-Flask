from EventCal.db import get_db


def get_all_calendars():
    # returns all calendars linked to events
    db = get_db()
    calendars = db.execute(
        'SELECT DISTINCT calendar FROM events ORDER BY calendar'
        ).fetchall()

    return tuple([row['calendar'] for row in calendars])


def get_all_locations():
    # return all locations linked to events
    db = get_db()
    locations = db.execute(
        'SELECT DISTINCT location FROM events ORDER BY location'
        ).fetchall()

    return tuple([row['location'] for row in locations])


def get_user_data(user):
    db = get_db()
    # returns all events calendars and locations of user
    cals = user['sub_calendars'].split(',')
    locs = user['sub_locations'].split(',')
    events = db.execute(
            'SELECT * FROM events WHERE calendar IN ({}) AND location IN ({})'.format(
                ','.join('?' for i in cals), ','.join('?' for i in locs)
                ), cals + locs
            ).fetchall()
    return (events, cals, locs)


def get_all_events():
    db = get_db()
    # returns all events in database
    events = db.execute(
            'SELECT * FROM events'
    ).fetchall()
    return events


def update_user(user, cal, loc):
    db = get_db()
    current_cals = user['sub_calendars'].split(',')
    current_locs = user['sub_locations'].split(',')

    # removing empty string from new user
    if not current_cals[0]:
        current_cals = []
    if not current_locs[0]:
        current_locs = []

    # if calendar of location given add or remove them from current list
    if cal is not None and cal:
        if cal in current_cals:
            current_cals.remove(cal)
        else:
            current_cals.append(cal)
    if loc is not None and loc:
        if loc in current_locs:
            current_locs.remove(loc)
        else:
            current_locs.append(loc)

    cals = ','.join(current_cals)
    locs = ','.join(current_locs)
    db.execute(
            'UPDATE users SET (sub_calendars, sub_locations) = (?, ?)'
            'WHERE user_id = ?', (cals, locs, user['user_id'])
            )
    db.commit()


def multiple_locations(user):
    current_locs = user['sub_locations'].split(',')
    if len(current_locs) > 1:
        return True
