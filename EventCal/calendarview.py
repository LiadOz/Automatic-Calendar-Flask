from flask import ( Blueprint, flash, g, redirect, url_for, render_template, request )
from werkzeug.exceptions import abort
from EventCal.auth import login_required
from EventCal.db import get_db
from EventCal.user_events import *
import os
import json

bp = Blueprint('events', __name__)
events_file = os.path.join(os.path.dirname(__file__), 'events.json')


@bp.route('/')
def index():

    all_cal = get_all_calendars()
    all_loc = get_all_locations()

    if g.user:
        events, user_cal, user_loc = get_user_data(g.user)
    else:
        events = get_all_events()
        user_cal = all_cal
        user_loc = all_loc

    create_data(events)
    return render_template('events/index.html', all_loc=all_loc, all_cal=all_cal, user_cal=user_cal, user_loc=user_loc)


@bp.route('/data')
def return_data():
    # read from the calendar
    start_date = request.args.get('start', '')
    end_date = request.args.get('end', '')
    with open(events_file, 'r') as input_data:
       return input_data.read()

@bp.route('/update/<string:up_type>/<string:val>')
@login_required
def update(up_type, val):

    if up_type == 'calendar':
        update_user(g.user, val, None)
    if up_type == 'location':
        update_user(g.user, None, val)

    return redirect(url_for('index'))

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

    with open(events_file, 'w') as f:
        json.dump(result, f)

