from flask import render_template, request
from flask.views import MethodView
import os
from dotenv import load_dotenv
import requests
import datetime
import re

class Index(MethodView):
    """
    Class representing the index page of the Flask app
    """
    
    def get(self):
        """
        HTTP GET method for displaying the index page
        """
        load_dotenv()
        search_query = request.args.get('query')
        tmdb_api_key = os.environ.get('TMDB_API_KEY')
        
        if search_query:
            return self.search_results(search_query, tmdb_api_key)
        else:
            return self.default_index_page(tmdb_api_key)
    


    def search_results(self, search_query, tmdb_api_key):
        tmdb_url = f'https://api.themoviedb.org/3/search/tv?api_key={tmdb_api_key}&query={search_query}'
        tmdb_response = requests.get(tmdb_url)
        
        if tmdb_response.status_code == 200:
            tmdb_data = tmdb_response.json()
            filtered_shows = self.filter_tmdb_data(tmdb_data)
            if filtered_shows:
                platforms_logos = self.get_platforms_logos(search_query)
                return render_template('result.html', shows=filtered_shows, platforms_logos=platforms_logos)
            else:
                return self.default_index_page_alert('Sorry, no show found with this name. Please try again!')
        else:
            return self.default_index_page()


    def filter_tmdb_data(self, tmdb_data):
        """
        Filter TMDB data to get relevant show information.
        """
        if 'results' in tmdb_data:
            filtered_shows = [
                {
                    'id': show['id'],
                    'name': show['name'],
                    'backdrop_path': show['backdrop_path'],
                    'poster_path': show['poster_path'],
                    'overview': show['overview'],
                    'first_air_date': show['first_air_date']
                }
                for show in tmdb_data['results']
            ]
            return filtered_shows
        else:
            return []

    def get_filtered_shows(tmdb_api_key):
        shows = []
        current_date = datetime.datetime.now()
        tomorrow = current_date + datetime.timedelta(days=1)
        months_later = current_date + datetime.timedelta(180)
        for single_date in (tomorrow + datetime.timedelta(n) for n in range(180)):
            tmdb_url = f"https://api.themoviedb.org/3/discover/tv?api_key={tmdb_api_key}&include_video=true&sort_by=popularity.desc&first_air_date.gte={single_date.strftime('%Y-%m-%d')}"
            tmdb_response = requests.get(tmdb_url)
            tmdb_data = tmdb_response.json()
            if 'results' in tmdb_data:
                for show in tmdb_data['results']:
                    if show.get('first_air_date', '') < tomorrow.strftime('%Y-%m-%d') or show.get('first_air_date', '') > months_later.strftime('%Y-%m-%d'):
                        continue
                    if not re.match(r'^[\x00-\x7F]+$', show['name']):
                        continue
                    video_url = f"https://api.themoviedb.org/3/tv/{show['id']}/videos?api_key={tmdb_api_key}"
                    video_response = requests.get(video_url)
                    video_data = video_response.json().get('results', [])

                    video_urls = []
                    video_titles = []
                    for video in video_data:
                        if 'site' in video and video['site'] == 'YouTube':
                            video_urls.append(f"https://www.youtube.com/watch?v={video['key']}")
                            video_titles.append(video['name'])
                    most_watched_video = sorted(video_titles)[-1] if video_titles else None
                    if most_watched_video:
                        show['video'] = {'title': most_watched_video, 'url': video_urls[video_titles.index(most_watched_video)]}
                        shows.append(show)
        
        return shows