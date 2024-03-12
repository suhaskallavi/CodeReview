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

