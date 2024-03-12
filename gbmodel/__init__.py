model_backend = 'datastore'

if model_backend == 'sqlite3':
    from .model_sqlite3 import model
elif model_backend == 'datastore':
    from .model_datastore import model
else:
    raise ValueError("No appropriate databackend configured.")

appmodel = model()

def get_model():
    """
    Get the instance of the model used by the application.

    Returns:
        model: The instance of the model.

    """
    return appmodel
