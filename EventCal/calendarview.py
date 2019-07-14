from flask import ( Blueprint, flash, g, redirect, url_for, render_template, request )
from werkzeug.exceptions import abort
from EventCal.auth import login_required
from EventCal.db import get_db
from EventCal.user_events import *

import json
bp = Blueprint('events', __name__)


@bp.route('/')
def index():

    if g.user:
        events, all_cal, all_loc = get_user_data(g.user)
    else:
        events = get_all_events()
        all_cal = get_all_calendars()
        all_loc = get_all_locations()

    create_data(events)
    return render_template('events/index.html', all_loc=all_loc, all_cal=all_cal)


@bp.route('/data')
def return_data():
    # read from the calendar
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    with open('EventCal/events.json', 'r') as input_data:
       return input_data.read()


@bp.route('/settings', methods=('GET', 'POST'))
@login_required
def settings():
    if request.method == 'POST':
        cal = request.form['calendar']
        loc = request.form['location']

        update_user(g.user, cal, loc)

        return redirect(url_for('events.index'))

    return render_template('events/settings.html')


def create_data(events):
    colors = {
            'Elections': ('blue', 'white'),
            'Video Games': ('red', 'white'),
            'Movies': ('yellow', 'black')
             }

    result = []

    # Determining whether to to add location to title
    if g.user:
        mult = multiple_locations(g.user)
    else:
        mult = True

    for ev in events:
        color = colors[ev['calendar']]
        if mult:
            title = '{} - {}'.format(ev['title'], ev['location'])
        else:
            title = ev['title']
        result.append({'title': title, 'start': ev['edate'], 'color': color[0], 'textColor': color[1]})

    with open('EventCal/events.json', 'w') as f:
        json.dump(result, f)

