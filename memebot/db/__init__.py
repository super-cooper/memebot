from memebot import config
from .internals import DatabaseInternals

db_internals = DatabaseInternals()


def test() -> bool:
    """
    Functions as a "ping" to the databse to ensure that there is an available connection
    :return: True if the test succeeds
    """
    if config.database_enabled:
        try:
            db_internals.client.server_info()  # type: ignore[union-attr]
        except Exception:
            return False
    return True
