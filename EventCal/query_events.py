from SPARQLWrapper import SPARQLWrapper, JSON
import datetime


def query_all():
    queries = (query_elections, query_movies, query_video_games)
    result = []
    for f in queries:
        result += f()

    return result


def _get_events(endpoint_url, query):
    sparql = SPARQLWrapper(endpoint_url, agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11")
    # Agent is used to bypass wikidata User-Agent policy (https://stackoverflow.com/questions/30755625/urlerror-with-sparqlwrapper-at-sparql-query-convert)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    result = sparql.query().convert()

    return result


def _create_event_tup(new_events, ev_type):
    new_events = new_events['results']['bindings']
    event_list = []
    for ev in new_events:
        if ev['descriptionLabel']['value'] == 'NO_DATA':
            # Emptying the description if doesn't exist
           ev['descriptionLabel']['value'] = ''

        event_list.append({
            'id': ev['title']['value'].split('/')[-1], 'calendar': ev_type, 'location': ev['locationLabel']['value'],
            'title':ev['titleLabel']['value'], 'description': ev['descriptionLabel']['value'], 'edate': ev['date']['value']
            })

    return tuple(event_list)


# Returns video games that will be released in the future in an array of dictionaries of each new game.
def query_video_games():
    q_site = "https://query.wikidata.org/sparql"
    query = """
    SELECT ?title ?titleLabel ?date ?locationLabel ?descriptionLabel WHERE {
      ?title wdt:P31 wd:Q7889;
        p:P577 ?time.
      ?time ps:P577 ?date.
      ?time psv:P577 ?timeNode.
      ?timeNode wikibase:timePrecision ?per.
      FILTER (?per >= 11)
      FILTER(?date >= (NOW()))

      BIND("worldwide" AS ?default_location)
      OPTIONAL { ?time pq:P291 ?location. }
      BIND(COALESCE(?location, ?default_location) AS ?location)
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
      BIND("NO_DATA" AS ?descriptionLabel)
    }
    ORDER BY (?date)
    """
    games = _get_events(q_site, query)
    return _create_event_tup(games, 'Video Games')


def query_elections():
    q_site = "https://query.wikidata.org/bigdata/namespace/wdq/sparql"
    query = """
    SELECT ?title ?titleLabel ?date ?locationLabel ?descriptionLabel WHERE {
      # Including General Elections, Presidential Elections, Primary Elections
      {?electionType wdt:P31*/wdt:P279* wd:Q1076105} UNION
      {?electionType wdt:P31*/wdt:P279* wd:Q858439} UNION
      {?electionType wdt:P31*/wdt:P279* wd:Q669262}

      # Getting all elections data
      ?title wdt:P31 ?electionType .
       ?title wdt:P17 ?location;
         wdt:P585 ?date;
        (p:P585/psv:P585) ?timenode;
      # Filtering passed and non accurate dates
      FILTER(?date >= (NOW()))
      ?timenode wikibase:timePrecision ?timePrecision.
      FILTER(?timePrecision >= 11 )

      # Filtering elections that are part of something else
      FILTER NOT EXISTS{?title wdt:P361 ?partOf}
      BIND(?electionType AS ?description)
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    ORDER BY (?date)
    """
    elections = _get_events(q_site, query)
    return _create_event_tup(elections, 'Elections')


def query_movies():
    q_site = "https://query.wikidata.org/sparql"
    query = """
    SELECT ?title ?titleLabel ?date ?locationLabel ?descriptionLabel WHERE {
    {
    SELECT ?title ?titleLabel ?date ?locationLabel
    WHERE
    {

      ?title wdt:P31 wd:Q11424;
            p:P577 ?statement. # Getting all release date locations.
      ?statement ps:P577 ?date.
      ?statement psv:P577 ?timenode.
      FILTER(?date >= now())

      BIND("worldwide" AS ?default_location)
      OPTIONAL { ?statement pq:P291 ?location. }
      BIND(COALESCE(?location, ?default_location) AS ?location)

      ?timenode wikibase:timePrecision ?timePrecision .
      FILTER (?timePrecision >= 11)

      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    }
    FILTER (!REGEX(?titleLabel, "^Q[0-9]+$")) # Filter those with no label.
    BIND("NO_DATA" AS ?descriptionLabel)
    }ORDER BY (?date)
    """
    movies = _get_events(q_site, query)
    return _create_event_tup(movies, 'Movies')


def xml_time_to_datetime(xml_time):
    return datetime.datetime.strptime(xml_time, "%Y-%m-%dT%H:%M:%Sz")

