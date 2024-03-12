from .Model import Model
from google.cloud import datastore

def from_datastore(entity):
    """
    Convert a Datastore entity into a list of attributes.

    Args:
        entity (google.cloud.datastore.Entity): The Datastore entity to convert.

    Returns:
        list: List of attributes extracted from the entity.

    """
    if not entity:
        return None
    if isinstance(entity, list):
        entity = entity.pop()
    return [
        entity['show_id'],
        entity['show_name'],
        entity['backdrop_path'],
        entity['poster_path'],
        entity['overview'],
        entity['first_air_date']
    ]


class model(Model):
    """
    A model class for interacting with the Datastore.

    Attributes:
        client (google.cloud.datastore.Client): The Datastore client.

    """

    def __init__(self):
        """
        Initialize the model by creating a Datastore client.
        """
        self.client = datastore.Client('cloud-dwarakanath-sd35')

    def select(self):
        """
        Retrieve all entities from the 'Shows' kind in the Datastore.

        Returns:
            list: List of entities retrieved from the Datastore.

        """
        query = self.client.query(kind='Shows')
        entities = list(map(from_datastore, query.fetch()))
        return entities

    def insert(self, show_id, show_name, backdrop_path, poster_path, overview, first_air_date):
        """
        Insert a new entity into the 'Shows' kind in the Datastore.

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
        key = self.client.key('Shows')
        show = datastore.Entity(key)
        show.update({
            'show_id': show_id,
            'show_name': show_name,
            'backdrop_path': backdrop_path,
            'poster_path': poster_path,
            'overview': overview,
            'first_air_date': first_air_date
        })
        self.client.put(show)
        return True

    def delete(self, show_id):
        """
        Delete an entity from the 'Shows' kind in the Datastore.

        Args:
            show_id (str): The ID of the TV show to delete.

        """
        query = self.client.query(kind='Shows')
        for entity in query.fetch():
            if entity['show_id'] == show_id:
                self.client.delete(entity.key)
