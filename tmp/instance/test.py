import pprint
import sqlite3


db = sqlite3.connect('Acal.sqlite')
db.row_factory = sqlite3.Row

def create_user(name, pas, cals, locs):
    if isinstance(cals, list):
        cals = ','.join(cals)
    if isinstance(locs, list):
        locs = ','.join(locs)
    db.execute(
            'INSERT INTO users (username, password, sub_calendars, sub_locations)'
            'VALUES (?, ?, ?, ?)', (name, pas, cals, locs) 
            )
    db.commit()
def create_users():
    create_user('Mac', '123', ['Karate', 'Trenchcoats', 'Gaybars', 'Gym'], ['Philly', 'Wisconsin'])
    create_user('Charlie', '123', ['Law', 'Crows', 'Toe knives', 'Musicals'], ['Philly'])
    create_user('Dennis', '123', ['Rape', 'Tools', 'Fish'], ['Philly', 'North-Dakotoa'])
    create_user('dee', '123', [], [])

def get_user(username):
    user = db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
            ).fetchone()
    if user is None:
        print('error')
        return None

    user = {'user_id': user['user_id'], 'username': user['username'], 'calendars': user['sub_calendars'].split(','), \
            'locations':user['sub_locations'].split(',')}

    return user

def update_user(user):
    if isinstance(user['sub_calendars'], list):
        user['sub_calendars'] = ','.join(user['sub_calendars'])
    if isinstance(user['sub_locations'], list):
        user['sub_locations'] = ','.join(user['sub_locations'])

    db.execute(
            'UPDATE users SET (sub_calendars, sub_locations) = (?, ?)'
            'WHERE user_id = ?', (user['sub_calendars'], user['sub_locations'], user['user_id'])
            )
    db.commit()

