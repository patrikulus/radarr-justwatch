import requests
import time
import os
import yaml
from justwatch import JustWatch
from pyarr import RadarrAPIv3

host_url = os.environ.get('RADARR_HOST_URL')
api_key = os.environ.get('RADARR_API_KEY')
country = os.environ.get('COUNTRY')

radarr = RadarrAPIv3(host_url, api_key)
just_watch = JustWatch(country=country)


def get_tag_from_url(url, tags):
    target_platform = ''
    config = dict()

    with open('config.yml', 'r') as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    for platform in config['platforms']:
        if url.startswith(platform['url']):
            target_platform = platform['name']
  
    if target_platform != '':
        return next(tag['id'] for tag in tags if tag['label'] == target_platform)
    return 0
    

tags = (requests.get(host_url + "/api/v3/tag?apiKey=" + api_key)).json()
movies = radarr.get_movie()


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