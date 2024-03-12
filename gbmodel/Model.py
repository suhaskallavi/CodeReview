class Model():
    """
    Abstract base class for a TV show model.

    """

    def select(self):
        """
        Retrieve all TV shows.

        Returns:
            list: List of TV shows.

        """
        pass

    def insert(self, show_id, show_name, backdrop_path, poster_path, overview, first_air_date):
        """
        Insert a new TV show.

        Args:
            show_id (str): The ID of the TV show.
            show_name (str): The name of the TV show.
            backdrop_path (str): The path to the backdrop image of the TV show.
            poster_path (str): The path to the poster image of the TV show.
            overview (str): The overview/description of the TV show.
            first_air_date (str): The date when the TV show first aired.

        Returns:
            bool: True if the insertion was successful.

        """
        pass

    def delete(self, show_id):
        """
        Delete a TV show.

        Args:
            show_id (str): The ID of the TV show to delete.

        Returns:
            bool: True if the deletion was successful.

        """
        pass
