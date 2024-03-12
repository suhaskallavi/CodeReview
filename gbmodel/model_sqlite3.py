"""
A simple TV show viewer Flask app.
Data is stored in a SQLite database that looks something like the following:

+------------+-----------------+--------------------------+-----------------------+-----------------+-----------------+
| Show ID    | Show Name       | Backdrop                 | Poster                | Overview        | First Air Date  |
+============+=================+==========================+=======================+=================+=================+
| 1          | Stranger Things | /path/to/backdrop.jpg    | /path/to/poster.jpg   | <Show Summary>  | 2016-07-15      |
+------------+-----------------+-+------------------------+-----------------------+-----------------+-----------------+

This can be created with the following SQL (see bottom of this file):

    create table shows (show_id text, show_name text, backdrop_path text, poster_path text, overview text, first_air_date text);

"""

from .Model import Model
import sqlite3

DB_FILE = 'mylist.db'

class model(Model):
    """
    A model class for interacting with a SQLite database.

    Attributes:
        connection (sqlite3.Connection): The connection to the SQLite database.

    """

    def __init__(self):
        """
        Initialize the model by establishing a connection to the SQLite database.
        If the 'shows' table does not exist, it will be created.
        """
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT COUNT(show_id) FROM shows")
        except sqlite3.OperationalError:
            cursor.execute("CREATE TABLE shows (show_id TEXT, show_name TEXT, backdrop_path TEXT, poster_path TEXT, overview TEXT, first_air_date TEXT)")
        cursor.close()

    def select(self):
        """
        Retrieve all shows from the 'shows' table in the SQLite database.

        Returns:
            list: List of shows retrieved from the database.

        """
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM shows")
        return cursor.fetchall()

    def insert(self, show_id, show_name, backdrop_path, poster_path, overview, first_air_date):
        """
        Insert a new show into the 'shows' table in the SQLite database.

        Args:
            show_id (str): The ID of the show.
            show_name (str): The name of the show.
            backdrop_path (str): The path to the backdrop image of the show.
            poster_path (str): The path to the poster image of the show.
            overview (str): The overview/description of the show.
            first_air_date (str): The date when the show first aired.

        Returns:
            bool: True if the insertion was successful.

        """
        params = {
            'show_id': show_id,
            'show_name': show_name,
            'backdrop_path': backdrop_path,
            'poster_path': poster_path,
            'overview': overview,
            'first_air_date': first_air_date
        }
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO shows (show_id, show_name, backdrop_path, poster_path, overview, first_air_date) VALUES (:show_id, :show_name, :backdrop_path, :poster_path, :overview, :first_air_date)", params)
        connection.commit()
        cursor.close()
        return True

    def delete(self, show_id):
        """
        Delete a show from the 'shows' table in the SQLite database.

        Args:
            show_id (str): The ID of the show to delete.

        Returns:
            bool: True if the deletion was successful.

        """
        connection = sqlite3.connect(DB_FILE)
        cursor = connection.cursor()
        cursor.execute("DELETE FROM shows WHERE show_id = ?", (show_id,))
        connection.commit()
        cursor.close()
        return True
