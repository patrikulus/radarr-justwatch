import requests
import time
import os
import yaml
from justwatch import JustWatch
from pyarr import RadarrAPIv3

radarr_host_url = os.environ.get('RADARR_HOST_URL')
radarr_api_key = os.environ.get('RADARR_API_KEY')
country = os.environ.get('COUNTRY')

radarr = RadarrAPIv3(radarr_host_url, radarr_api_key)
just_watch = JustWatch(country=country)
config = dict()
tags = dict()


def init():
    load_config()
    load_tags()

    movies = radarr.get_movie()

    for movie in movies:
        process_movie(movie)

def load_config():
    global config
    with open('config.yml', 'r') as stream:
        try:
            config = yaml.safe_load(stream)
            return config
        except yaml.YAMLError as exc:
            print(exc)

def load_tags():
    global tags
    tags = (requests.get(radarr_host_url + "/api/v3/tag?apiKey=" + radarr_api_key)).json()

def process_movie(movie):
    print(movie['title'])
    
    jw_movie = get_matching_movie(movie['title'], movie['tmdbId'])

    if 'offers' in jw_movie.keys():
        tag_streaming_platforms(movie, jw_movie['offers'])


def get_matching_movie(title, tmdbid):
    jw_movie = dict()
    scoring_marker = {
        'provider_type': 'tmdb:id',
        'value': tmdbid
    }

    jw_collection = search_for_movie(title)
    
    if len(jw_collection) > 0:
        jw_matching_movies = list(filter(lambda item: item['object_type'] == 'movie' and 'scoring' in item.keys() and scoring_marker in item['scoring'], jw_collection))
        
        if len(jw_matching_movies) > 0:
            jw_movie = jw_matching_movies[0]

    return jw_movie


def search_for_movie(title):
    results = []

    # delay to avoid api call limits
    time.sleep(1)
    jw_search = just_watch.search_for_item(query=title)

    if len(jw_search['items']) > 0:
        results = jw_search['items']

    return results


def tag_streaming_platforms(movie, platforms):
    streaming_platforms = list(filter(lambda offer: offer['monetization_type'] == 'flatrate', platforms))

    for streaming_platform in streaming_platforms:
        print(streaming_platform['urls']['standard_web'])
        tag_id = get_tag_from_url(streaming_platform['urls']['standard_web'])
        
        if tag_id != 0 and tag_id not in movie['tags']:
            movie['tags'].append(tag_id)
            radarr.update_movie(movie)


def get_tag_from_url(url):
    target_platform = ''

    for platform in config['platforms']:
        if url.startswith(platform['url']):
            target_platform = platform['name']
  
    if target_platform != '':
        return next(tag['id'] for tag in tags if tag['label'] == target_platform)
    return 0
    

def reset_tags(movies):
    for movie in movies:
        movie['tags'] = []
        radarr.update_movie(movie)


init()