from flask import redirect, request, url_for, render_template
from flask.views import MethodView
import gbmodel

class AddList(MethodView):
    """A class representing a view for adding shows to a list."""

    def post(self):
        """Handle POST requests to add a show to the list.

        Args:
            show_id (int): The ID of the show.
            show_name (str): The name of the show.
            backdrop_path (str): The path to the backdrop image of the show.
            poster_path (str): The path to the poster image of the show.
            overview (str): A brief overview of the show.
            first_air_date (str): The first air date of the show.

        Returns:
            A redirect response to the home page.
        """
        data = request.get_json()
        show_id = data.get('show_id')
        show_name = data.get('show_name')
        backdrop_path = data.get('backdrop_path')
        poster_path = data.get('poster_path')
        overview = data.get('overview')
        first_air_date = data.get('first_air_date')
        model = gbmodel.get_model()
        shows = [
            dict(
                show_id=row[0],
                show_name=row[1],
                backdrop_path=row[2],
                poster_path=row[3],
                overview=row[4],
                first_air_date=row[5]
            )
            for row in model.select()
        ]

        # Check if the show is already in the list, if not, add it
        if not any(show['show_id'] == show_id for show in shows):
            model.insert(show_id, show_name, backdrop_path, poster_path, overview, first_air_date)
        return redirect(url_for('index'))
