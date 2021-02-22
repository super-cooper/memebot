import config
from .internals import DatabaseInternals

db_internals = DatabaseInternals()

if config.database_enabled:
    db_internals.connect()


def test() -> bool:
    """
    Functions as a "ping" to the databse to ensure that there is an available connection
    :return: True if the test succeeds
    """
    test_db = db_internals.get_db("test")
    test_db.list_collection_names()
    return True
