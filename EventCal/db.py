import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext
from EventCal.query_events import query_all


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
            )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def update_db():
    db = get_db()
    events = tuple(query_all())
    db.executemany(
            'INSERT OR REPLACE INTO events (id, calendar, location, title, description, edate) '
            'VALUES (:id, :calendar, :location, :title, :description, :edate)', events[:253]
            )
    db.commit()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(update_db_command)


@click.command('init-db')
@with_appcontext
def init_db_command():
    # Clear db and create new tables
    init_db()
    click.echo('Initialized the database')


@click.command('update-db')
@with_appcontext
def update_db_command():
    # Update events in the database
    click.echo('Updating database...')
    update_db()
    click.echo('Updated the database')

