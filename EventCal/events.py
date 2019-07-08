import json
import datetime
import query_events


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

create_user('Mac', '123', ['Karate', 'Trenchcoats', 'Gaybars', 'Gym'], ['Philly', 'Wisconsin'])
create_user('Charlie', '123', ['Law', 'Crows', 'Toe knives', 'Musicals'], ['Philly'])
create_user('Dennis', '123', ['Rape', 'Tools', 'Fish'], ['Philly', 'North-Dakotoa'])
create_user('dee', '123', [], [])

def get_user(id):
    user = db.execute(
            'SELECT * FROM users WHERE user_id= ?', (id,)
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

dee = get_user('Dee')
print(type(dee))
dee['sub_calendars'] = ['Standup Comedy', 'Birds']
dee['sub_locations'] = ['Philly']
update_user(dee)
print(get_user('Dee'))

class EventTracker:
    """
    Represents an event tracker, uses json file to store the information in groups according to categories
    defines subscriptions and locations list, the user can subscribe to categories and locations with the subscribe_to
    and add_locations method then use the update_subscriptions method to update it's calendar.
    the locations and subscriptions are stored with lower case.
    The events are stored as Event object defined below in a dictionary which stores lists of events according to it's
    category in sorted order.
    When the user has finished manipulating the calendar it is saved with save_event_tracker method.
    In order to keep new events for the users to get, the method update_main_file needs to be called at a suitable
    interval.
    """


    def __init__(self, user):
        """
        Creates a new user based of sqlite3.Row object
        :param user: sqlite3.Row object reprenting the user
        """
        self.sub_calendars = user['sub_calendars'].split(',')
        self.sub_locations = user['sub_locations'].split(',')

    def __init___old(self, file_name='user1.json'):
        self.sub_calendars = []
        self.available_calendars = []
        self.sub_locations = []
        self.available_locations = set()

        self.file_name = file_name
        self.event_dict = {}
        self.update_events_from_file()

    def __str___old(self):
        st = ''
        for category, events in self.event_dict.items():
            st += category + '\n\n'
            for ev in events:
                st += (ev.__str__() + '\n')
        return st

    def add_subscription_old(self, category):
        if category not in self.sub_calendars:
            self.sub_calendars.append(category.lower())
            self.available_calendars.remove(category.lower())

    def remove_subscription_old(self, category):
        category = category.lower()
        if category not in self.sub_calendars:
            return

        self.sub_calendars.remove(category)
        self.available_calendars.append(category)
        # Removing the category's events.
        self.event_dict.pop(category)

    def add_location_old(self, location):
        if location not in self.sub_locations:
            self.sub_locations.append(location.lower())
            self.available_locations.remove(location.lower())

    def remove_location_old(self, location):
        location = location.lower()
        if location not in self.sub_locations:
            return

        self.sub_locations.remove(location)
        self.available_locations.append(location)
        for key in self.event_dict:
            self.event_dict[key] = list(filter(lambda ev: ev.location != location, self.event_dict[key]))

    def update_subscriptions_old(self):
        master = EventTracker(self.database_name)
        events_to_add = []

        # if all subscribed to all
        if self.ALL_ENTRIES in self.sub_calendars:
            for ev_list in master.event_dict.values():
                for event in ev_list:
                    if event.location in self.sub_locations or self.ALL_ENTRIES in self.sub_locations:
                        events_to_add.append(event)
            self.add_events(events_to_add)
            return

        for sub in self.sub_calendars:
            if sub in master.event_dict:
                events = master.event_dict[sub]
                for event in events:
                    if event.location in self.sub_locations or self.ALL_ENTRIES in self.sub_locations:
                        events_to_add.append(event)
        self.add_events(events_to_add)

    def update_events_from_file_old(self):

        self.event_dict = {}
        read = self.read_event_tracker(self.file_name)
        if read is None:
            return

        self.sub_calendars = read['user_data']['sub_calendars']
        self.sub_locations = read['user_data']['sub_locations']
        try:
            self.available_calendars = read['user_data']['available_calendars']
            self.available_locations = set(read['user_data']['available_locations'])
        except KeyError:  # In case file is in the old format
            subloc = self.get_all_subscriptions_and_locations()

            for sub in self.sub_calendars:  # Removing the existing subscriptions
                if sub in subloc[0]:
                    subloc[0].remove(sub)
            for loc in self.sub_locations:  # Removing the existing locations
                if loc in subloc[1]:
                    subloc[1].remove(loc)

            self.available_calendars = subloc[0]
            self.available_locations = subloc[1]

        for ev_dict in read['events'].items():
            self.event_dict[ev_dict[0]] = []
            for ev in ev_dict[1]:
                self.event_dict[ev_dict[0]].append(Event(**ev))

    def add_raw_events_old(self,ev_list):
        """
        Adds events from dictionary items.
        :param ev_list: list of dictionaries.
        """
        count = 0
        for event in ev_list:
            if self.__add_mult_events(Event(**event)):
                count += 1
        print(count)
        self.sort_events()

    def add_events_old(self,ev_list):
        """
        Adds events from event items.
        :param ev_list: list of events.
        """
        count = 0
        for event in ev_list:
            if self.__add_mult_events(event):
                count += 1
        print(count)
        self.sort_events()

    def add_event_old(self, ev):
        """
        Adds event to the tracker.
        :param ev: Event object.
        """
        assert isinstance(ev, Event)

        if ev.ev_type not in self.event_dict:
            self.event_dict[ev.ev_type] = []
            self.event_dict[ev.ev_type].append(ev.__copy__())
            print('event added')
            print(ev)
            return True

        if ev in self.event_dict[ev.ev_type]:
            return False

        for event in self.event_dict[ev.ev_type]:
            if event.update(ev):
                print('event updated')
                print(event)
                return True

        self.event_dict[ev.ev_type].append(ev.__copy__())
        print('event added')
        print(ev)
        self.sort_events()
        return True

    def __add_mult_events_old(self, ev):
        """
        Adds event to the tracker.
        Used when a couple of events are added to make less sorts.
        :param ev: Event object.
        """
        assert isinstance(ev, Event)

        if ev.ev_type not in self.event_dict:
            self.event_dict[ev.ev_type] = []
            self.event_dict[ev.ev_type].append(ev.__copy__())
            print('event added')
            print(ev)
            return True

        if ev in self.event_dict[ev.ev_type]:
            return False

        for event in self.event_dict[ev.ev_type]:
            if event.update(ev):
                print('event updated')
                print(event)
                return True

        self.event_dict[ev.ev_type].append(ev.__copy__())
        print('event added')
        print(ev)
        return True

    def save_event_tracker_old(self, aux_data= {}):
        """
        Saves the events in the Event Tracker.
        """
        save = {'user_data': {}, 'events': {}, 'aux_data': aux_data}

        save['user_data'].update({'sub_calendars': self.sub_calendars})
        save['user_data'].update({'sub_locations': self.sub_locations})
        save['user_data'].update({'available_calendars': self.available_calendars})
        locations = list(self.available_locations)
        locations.sort()
        save['user_data'].update({'available_locations': locations})

        for ev_dict in self.event_dict.items():
            save['events'].update({ev_dict[0]: []})
            for ev in ev_dict[1]:
                save['events'][ev_dict[0]].append(ev.__dict__)

        with open('web//users//' + self.file_name, 'w') as file:
            json.dump(save, file, indent=4, default=Event.serialize_date)

    @classmethod
    def read_event_tracker_old(cls, file):
        try:
            with open('web//users//' + file) as file:
                return json.load(file)
        except FileNotFoundError:
            return None

    def sort_events_old(self):
        """
        Sort the events by time.
        """
        for ev_list in self.event_dict.values():
            ev_list.sort(key=lambda x: x.time_since_epoch())

    def get_all_locations_old(self):
        locations = set()
        """
        :return: Returns all events locations in the tracker 
        """
        for ev_list in self.event_dict.values():
            for event in ev_list:
                if event.location not in locations:
                    locations.add(event.location)
        loc_list = list(locations)
        loc_list.sort()
        return loc_list

    @classmethod
    def update_main_file_old(cls):
        main_tracker = EventTracker(cls.database_name)
        main_tracker.add_subscription(main_tracker.ALL_ENTRIES)
        main_tracker.add_location(main_tracker.ALL_ENTRIES)
        main_tracker.add_raw_events(query_events.query_elections())
        main_tracker.add_raw_events(query_events.query_video_games())
        main_tracker.add_raw_events(query_events.query_movies())

        util_data ={'all_subscriptions':['elections', 'video_games', 'movies'],
                    'all_locations':main_tracker.get_all_locations()}

        main_tracker.save_event_tracker(util_data)

    @classmethod
    def get_all_subscriptions_and_locations_old(cls):
        """
        :return: Returns all subscriptions and locations available from main file, it returns a list with 2 sublists
        the first one is all of the subscriptions and the second one is the locations list.
        """
        read = cls.read_event_tracker(cls.database_name)
        return [read['aux_data']['all_subscriptions'], set(read['aux_data']['all_locations'])]


class Event:

    title = ''
    description = ''
    date = None
    location = ''

    def __init__(self, title, date, location, ev_type, description=''):
        self.title = title
        self.description = description
        self.location = location
        self.ev_type = ev_type
        if isinstance(date, datetime.datetime):
            self.date = date
        else:
            self.date = datetime.datetime(*date)

    def __copy__(self):
        return Event(self.title, self.date, self.location, self.ev_type, self.description)

    def __str__(self):
        return 'Title: {} \nDate: {} \nDescription: {} \nLocation {} \n'.format(
            self.title, self.date, self.description, self.location)

    def __eq__(self, other):
        # If the object is updated we currently create another one
        assert isinstance(other, Event)
        return self.title == other.title and self.description == other.description and \
            self.date == other.date and self.location == other.location and self.ev_type == other.ev_type

    def update(self, other):
        assert isinstance(other, Event)
        if self != other and self.title == other.title and\
                self.location == other.location and self.ev_type == other.ev_type:
            self.description = other.description
            self.date = other.date
            self.location = other.location
            return True
        return False

    def time_until(self):
        """
        Tells the days until the events ends.
        :return:  Days until the event ends.
        """
        time = self.date - datetime.datetime.now()
        if time.total_seconds() < 0:
            return "Date passed"
        return time.days.__str__() + ' days left'

    def time_since_epoch(self):
        """
        :return: Time since epoch
        """
        try:
            return self.date.timestamp()
        except OSError:
            return -1

    @staticmethod
    def serialize_date(o):
        if isinstance(o, datetime.datetime):
            return [o.year, o.month, o.day, o.hour, o.minute, o.second, o.microsecond, o.tzname()]
