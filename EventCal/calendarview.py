from flask import ( Blueprint, flash, g, redirect, url_for, render_template, request )
from werkzeug.exceptions import abort

from Acal.auth import login_required
from Acal.db import get_db
import json

bp = Blueprint('events', __name__)


@bp.route('/')
def index():
    db = get_db()

    all_cal = db.execute('SELECT DISTINCT calendar FROM events').fetchall()
    all_loc = db.execute('SELECT DISTINCT location FROM events').fetchall()
    all_cal = tuple([row['calendar'] for row in all_cal])
    all_loc = tuple([row['location'] for row in all_loc])

    if g.user:
        cals = tuple(g.user['sub_calendars'].split(','))
        locs = tuple(g.user['sub_locations'].split(','))
        # Checks available events according to user Calendars and Locations
        events = db.execute(
                'SELECT * FROM events WHERE calendar IN ({}) AND location IN ({})'.format(
                    ','.join('?' for i in cals), ','.join('?' for i in locs)
                    ), cals + locs
                ).fetchall()
    else:
        events = db.execute(
                'SELECT * FROM events'
        ).fetchall()

    create_data(events)
    return render_template('events/index.html', all_loc=all_loc, all_cal=all_cal)


@bp.route('/data')
def return_data():
    # read from the calendar
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    with open('Acal/events.json', 'r') as input_data:
       return input_data.read()


@bp.route('/settings', methods=('GET', 'POST'))
@login_required
def settings():
    if request.method == 'POST':
        cal = request.form['calendar']
        loc = request.form['location']

        cals = g.user['sub_calendars'].split(',')
        locs = g.user['sub_locations'].split(',')
        if cal is not None:
            cals.append(cal)
        if loc is not None:
            locs.append(loc)

        print(cal)
        cal = ','.join(cals)
        loc = ','.join(locs)

        db = get_db()
        db.execute(
                'UPDATE users SET (sub_calendars, sub_locations) = (?, ?)'
                'WHERE user_id = ?', (cal, loc, g.user['user_id'])
                )
        db.commit()
        return redirect(url_for('events.index'))

    return render_template('events/settings.html')


def create_data(events):
    colors = {
            'Elections': ('blue', 'white'),
            'Video Games': ('red', 'white'),
            'Movies': ('yellow', 'black')
            }

    result = []
    for ev in events:
        color = colors[ev['calendar']]
        result.append({'title': '{} - {}'.format(ev['title'], ev['location']), 'start': ev['edate'],
            'color': color[0], 'textColor': color[1]})

    with open('Acal/events.json', 'w') as f:
        glob = json.dumps(result)
        json.dump(result, f)

