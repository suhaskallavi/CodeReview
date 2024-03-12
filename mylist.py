from flask import render_template, request, redirect, url_for
from flask.views import MethodView
import gbmodel

class MyList(MethodView):
    """A class representing a view for displaying and managing a list of shows."""

    def get(self):
        """Handle GET requests to display the list of shows.

        Returns:
            A rendered template with the list of shows.
        """
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

        return render_template('mylist.html', shows=shows)

    def post(self):
        """Handle POST requests to delete a show from the list.

        Returns:
            A redirect response to the updated list of shows.
        """
        show_id = request.form.get('show_id')
        model = gbmodel.get_model()
        model.delete(show_id)
        return redirect(url_for('mylist'))
