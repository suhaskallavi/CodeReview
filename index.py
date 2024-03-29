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

    def get_platforms_logos(self, search_query):
        """
        Retrieve streaming platforms and their logos.
        """
        rapid_url = "https://streaming-availability.p.rapidapi.com/v2/search/title"
        querystring = {"title":search_query,"country":"us","show_type":"series","output_language":"en"}
        rapid_headers = {
            "X-RapidAPI-Key": os.environ.get('RAPID_API_KEY'),
            "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"
        }
        rapid_response = requests.get(rapid_url, headers=rapid_headers, params=querystring)
        rapid_response_data = rapid_response.json()
        output = rapid_response_data.get('result', [])
        
        platforms = []
        for item in output:
            streaming_info = item.get('streamingInfo', {})
            if 'us' in streaming_info:
                platforms.extend(streaming_info['us'].keys())
                break
        
        logos = []
        brand_headers = {"accept": "application/json","Referer": "https://example.com/searchIntegrationPage"}
        for platform in platforms:
            brand_url = f"https://api.brandfetch.io/v2/search/{platform}"
            brand_response = requests.get(brand_url, headers=brand_headers)
            brand_response_data = brand_response.json()
            if brand_response_data:
                logo_url = brand_response_data[0].get('icon', '')
                if logo_url:
                    logos.append((platform, logo_url))
        
        return logos

    def default_index_page(self, tmdb_api_key):
        """
        Display default index page with upcoming shows.
        """
        shows = self.get_filtered_shows(tmdb_api_key)
        return render_template('index.html', shows=shows)

    def get_filtered_shows(self, tmdb_api_key):
        """
        Filter upcoming shows based on certain criteria.
        """
        shows = []
        current_date = datetime.date.today()
        tomorrow = current_date + datetime.timedelta(days=1)
        months_later = current_date + datetime.timedelta(days=6 * 30)
        start_date = tomorrow.strftime('%Y-%m-%d')
        end_date = months_later.strftime('%Y-%m-%d')
        
        tmdb_url = f'https://api.themoviedb.org/3/discover/tv?api_key={tmdb_api_key}&include_video=true&sort_by=popularity.desc&first_air_date.gte={start_date}&first_air_date.lte={end_date}'
        tmdb_response = requests.get(tmdb_url)
        tmdb_data = tmdb_response.json().get('results', [])
        
        for show in tmdb_data:
            if 'first_air_date' not in show or show['first_air_date'] < start_date or show['first_air_date'] > end_date or not re.match(r'^[\x00-\x7F]+$', show['name']):
                continue
            
            tv_id = show['id']
            video_url = f'https://api.themoviedb.org/3/tv/{tv_id}/videos?api_key={tmdb_api_key}'
            video_response = requests.get(video_url)
            video_data = video_response.json().get('results', [])
            
            video_urls = [f"https://www.youtube.com/watch?v={video['key']}" for video in video_data if video['site'] == 'YouTube']
            video_titles = [video['name'] for video in video_data if video['site'] == 'YouTube']
            filtered_videos = [{'title': title, 'url': url} for title, url in zip(video_titles, video_urls) if 'trailer' not in title.lower()]
            
            most_watched_video = []
            if filtered_videos:
                most_watched_video.append(max(filtered_videos, key=lambda video: video['title']))
                show['video'] = most_watched_video
                for video in show['video']:
                    video_id = re.search(r'(?<=v=)[^&#]+', video['url'])
                    if video_id:
                        video['video_id'] = video_id.group(0)
                shows.append(show)
        
        return shows
    
    def default_index_page_alert(self, alertMsg):
        """
        Display default index page with an alert message.
        """
        shows = self.get_filtered_shows(os.environ.get('TMDB_API_KEY'))
        return render_template('index.html', shows=shows, alertMsg=alertMsg)