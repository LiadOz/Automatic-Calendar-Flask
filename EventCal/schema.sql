DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS events;

CREATE TABLE users (
  user_id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL COLLATE nocase,
  password TEXT NOT NULL,
  sub_calendars TEXT DEFAULT '', 
  sub_locations TEXT DEFAULT ''
);
CREATE TABLE events (
  id TEXT,
  calendar TEXT,
  location TEXT,
  title TEXT,
  description TEXT,
  edate TEXT,
  PRIMARY KEY(id, location)
); 
