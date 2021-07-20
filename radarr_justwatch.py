import requests
import time
import os
from justwatch import JustWatch
from pyarr import RadarrAPIv3

host_url = 'http://localhost:7878'
api_key = os.environ.get('RADARR_API_KEY')

radarr = RadarrAPIv3(host_url, api_key)
just_watch = JustWatch(country='PL')

# results = just_watch.search_for_item(query='wanted')

# Import SonarrAPI Class

# Set Host URL and API-Key

# You can find your API key in Settings > General.

def get_tag_from_url(url, tags):
    platform = ''
    if url.startswith('http://www.netflix.com'):
        platform = 'netflix'
    if url.startswith('https://hbogo.pl'):
        platform = 'hbogo'
    if url.startswith('https://app.primevideo.com'):
        platform = 'primevideo'
    if url.startswith('https://www.horizon.tv'):
        platform = 'horizon'
    if url.startswith('https://player.pl'):
        platform = 'player'
    
    if platform != '':
        return list(filter(lambda tag: tag['label'] == platform, tags))[0]['id']
    return 0
    
     


# movie = radarr.get_movie(343668)
# movie[0]['tags'].append(4)
# radarr.update_movie(movie[0])


tags = (requests.get(host_url + "/api/v3/tag?apiKey=" + api_key)).json()
movies = radarr.get_movie()
# movies = radarr.lookup_movie("Matrix Reloaded")
# jw_test = just_watch.search_title_id(8909)
# reset tags
# for movie in movies:
#     movie['tags'] = []
#     radarr.update_movie(movie)


for movie in movies:
    title = movie['title']
    print(title)

    # delay to avoid api call limit
    time.sleep(1)
    jw_search = just_watch.search_for_item(query=title)

    if len(jw_search['items']) > 0:
        scoring_marker = {
            'provider_type': 'tmdb:id',
            'value': movie['tmdbId']
        }

        jw_matching_movies = list(filter(lambda item: item['object_type'] == 'movie' and 'scoring' in item.keys() and scoring_marker in item['scoring'], jw_search['items']))
        
        if len(jw_matching_movies) > 0:
            jw_movie = jw_matching_movies[0]

            if 'offers' in jw_movie.keys():
                streaming_platforms = list(filter(lambda offer: offer['monetization_type'] == 'flatrate', jw_movie['offers']))

                for platform in streaming_platforms:
                    print(platform['urls']['standard_web'])
                    tag_id = get_tag_from_url(platform['urls']['standard_web'], tags)
                    
                    if tag_id != 0:
                        if tag_id not in movie['tags']:
                            movie['tags'].append(tag_id)
                            radarr.update_movie(movie)
                    
                    print("end_loop")

print("end")