from flask import render_template, request
from flask.views import MethodView
import os
from dotenv import load_dotenv
import requests
import datetime
import re

class Index(MethodView):
    """
    Class representing the index page of the Flask app.

    """
    def get(self):
        """
        HTTP GET method for displaying the index page.

        Returns:
            str: Rendered template for the index page.

        """

        # Get the search query from the URL
        search = request.args.get('query')

        shows = []

        load_dotenv()
        tmdb_api_key = os.environ['TMDB_API_KEY']
        
        if search:
            
            tmdb_url = f'https://api.themoviedb.org/3/search/tv?api_key={tmdb_api_key}&query={search}'

            tmdb_response = requests.get(tmdb_url)

            if tmdb_response.status_code == 200:

                tmdb_data = tmdb_response.json()

                if len(tmdb_data['results']) > 0:

                    # getting the first result                    
                    filtered_shows = [
                        {
                            'id': tmdb_data['results'][0]['id'],
                            'name': tmdb_data['results'][0]['name'],
                            'backdrop_path': tmdb_data['results'][0]['backdrop_path'],
                            'poster_path': tmdb_data['results'][0]['poster_path'],
                            'overview': tmdb_data['results'][0]['overview'],
                            'first_air_date': tmdb_data['results'][0]['first_air_date']
                        }
                    ]

                    # proceed if there are any shows
                    if len(filtered_shows) > 0:
                        for show in filtered_shows:
                            tv_id = show['id']
                            video_url = f'https://api.themoviedb.org/3/tv/{tv_id}/videos?api_key={tmdb_api_key}'
                            video_response = requests.get(video_url)
                            video_data = video_response.json()

                            # get the video urls and titles
                            video_urls = [f"https://www.youtube.com/watch?v={video['key']}" for video in video_data['results'] if video['site'] == 'YouTube']
                            video_titles = [video['name'] for video in video_data['results'] if video['site'] == 'YouTube']

                            # zip the urls and titles together
                            filtered_videos = [{'title': title, 'url': url} for title, url in zip(video_titles, video_urls)] #if 'trailer' not in title.lower()]


                            # proceed if there are any videos
                            if len(filtered_videos) > 0:
                                
                                show['video'] = filtered_videos

                                # get the video ids
                                for video in show['video']:
                                    video_id = re.search(r'(?<=v=)[^&#]+', video['url'])
                                
                                    if video_id:
                                        video_id = video_id.group(0)
                                    else:
                                        continue

                                    video['video_id'] = video_id

                                shows.append(show)
                            else:
                                continue

                    # api for getting the streaming platforms
                    rapid_url = "https://streaming-availability.p.rapidapi.com/v2/search/title"

                    querystring = {"title":search,"country":"us","show_type":"series","output_language":"en"}
                
                    rapid_headers = {
                        "X-RapidAPI-Key": os.environ['RAPID_API_KEY'],
                        "X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"
                        }
                    
                    rapid_response = requests.get(rapid_url, headers=rapid_headers, params=querystring)
                    
                    rapid_response_data = rapid_response.json()
                    
                    output = (rapid_response_data['result'])
                    
                    key_names = []

                    # get the platforms                    
                    for i in range(len(output)):
                        streaming_info = output[i]['streamingInfo']
                        if 'us' in streaming_info:
                            us_platforms = streaming_info['us']
                            key_names.extend(us_platforms.keys())
                            break

                    # remove duplicates
                    platforms = list(set(key_names))

                    # api for getting the logos
                    brand_headers = {
                        "accept": "application/json",
                        "Referer": "https://example.com/searchIntegrationPage"
                        }
                    
                    logos = []

                    # get the logos
                    for platform in platforms:
                        brand_url = f"https://api.brandfetch.io/v2/search/{platform}"
                    
                        brand_response = requests.get(brand_url, headers=brand_headers)
                
                        brand_response_data = brand_response.json()

                        if brand_response_data:
                            logo_url = brand_response_data[0]['icon']
                            if logo_url:
                                logos.append(logo_url)

                    # zip the platforms and logos together
                    platforms_logos = zip(platforms, logos)

                    return render_template('result.html', shows=shows, platforms_logos=platforms_logos)

                # if no shows found                
                else:
                    return self.defaultIndexPageAlert('Sorry, no show found with this name. Please try again!')
            
            # if tmdb api fails
            else:
                return self.defaultIndexPage()

        # if no search query
        else:
            return self.defaultIndexPage()
    
    
    
    def defaultIndexPage(self):
        """
        Helper method for displaying the default index page.

        Returns:
            str: Rendered template for the default index page.

        """

        shows = []

        tmdb_api_key = os.environ['TMDB_API_KEY']

        current_date = datetime.date.today()
        tomorrow = current_date + datetime.timedelta(days=1)
        months_later = current_date + datetime.timedelta(days=6 * 30)

        start_date = tomorrow.strftime('%Y-%m-%d')
        end_date = months_later.strftime('%Y-%m-%d')

        tmdb_url = f'https://api.themoviedb.org/3/discover/tv?api_key={tmdb_api_key}&include_video=true&sort_by=popularity.desc&first_air_date.gte={start_date}&first_air_date.lte={end_date}'

        tmdb_response = requests.get(tmdb_url)

        tmdb_data = tmdb_response.json()
        if 'results' in tmdb_data:

            # filter the shows based on the criteria
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
                if show['first_air_date'] >= start_date
                and show['first_air_date'] <= end_date
                and re.match(r'^[\x00-\x7F]+$', show['name'])
            ]

            if len(filtered_shows) > 0:
                for show in filtered_shows:
                    tv_id = show['id']
                    video_url = f'https://api.themoviedb.org/3/tv/{tv_id}/videos?api_key={tmdb_api_key}'
                    video_response = requests.get(video_url)
                    video_data = video_response.json()

                    video_urls = [f"https://www.youtube.com/watch?v={video['key']}" for video in video_data['results'] if video['site'] == 'YouTube']
                    video_titles = [video['name'] for video in video_data['results'] if video['site'] == 'YouTube']

                    filtered_videos = [{'title': title, 'url': url} for title, url in zip(video_titles, video_urls) if 'trailer' not in title.lower()]

                    most_watched_video = []

                    if len(filtered_videos) > 0:
                            
                        most_watched_video.append(max(filtered_videos, key=lambda video: video['title']))
                        show['video'] = most_watched_video

                        video_id = []

                        for video in show['video']:
                            video_id = (re.search(r'(?<=v=)[^&#]+', video['url']))
                            
                            if video_id:
                                video_id = video_id.group(0)

                            else:
                                continue

                            video['video_id'] = video_id

                        shows.append(show)
                    else:
                        continue

        return render_template('index.html', shows=shows)
    
    def defaultIndexPageAlert(self,alertMsg):
        """
        Helper method for displaying the default index page with an alert message.

        Args:
            alertMsg (str): Alert message to display.

        Returns:
            str: Rendered template for the default index page with the alert message.

        """

        shows = []

        alertMsg = alertMsg

        tmdb_api_key = os.environ['TMDB_API_KEY']

        current_date = datetime.date.today()
        tomorrow = current_date + datetime.timedelta(days=1)
        months_later = current_date + datetime.timedelta(days=6 * 30)

        start_date = tomorrow.strftime('%Y-%m-%d')
        end_date = months_later.strftime('%Y-%m-%d')

        tmdb_url = f'https://api.themoviedb.org/3/discover/tv?api_key={tmdb_api_key}&include_video=true&sort_by=popularity.desc&first_air_date.gte={start_date}&first_air_date.lte={end_date}'

        tmdb_response = requests.get(tmdb_url)

        tmdb_data = tmdb_response.json()
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
                if show['first_air_date'] >= start_date
                and show['first_air_date'] <= end_date
                and re.match(r'^[\x00-\x7F]+$', show['name'])
            ]

            if len(filtered_shows) > 0:
                for show in filtered_shows:
                    tv_id = show['id']
                    video_url = f'https://api.themoviedb.org/3/tv/{tv_id}/videos?api_key={tmdb_api_key}'
                    video_response = requests.get(video_url)
                    video_data = video_response.json()

                    video_urls = [f"https://www.youtube.com/watch?v={video['key']}" for video in video_data['results'] if video['site'] == 'YouTube']
                    video_titles = [video['name'] for video in video_data['results'] if video['site'] == 'YouTube']

                    filtered_videos = [{'title': title, 'url': url} for title, url in zip(video_titles, video_urls) if 'trailer' not in title.lower()]

                    most_watched_video = []

                    if len(filtered_videos) > 0:
                            
                        most_watched_video.append(max(filtered_videos, key=lambda video: video['title']))
                        show['video'] = most_watched_video

                        video_id = []

                        for video in show['video']:
                            video_id = (re.search(r'(?<=v=)[^&#]+', video['url']))
                            
                            if video_id:
                                video_id = video_id.group(0)

                            else:
                                continue

                            video['video_id'] = video_id

                        shows.append(show)
                    else:
                        continue

        # returning the rendered template with the alert message
        return render_template('index.html', shows=shows, alertMsg=alertMsg)