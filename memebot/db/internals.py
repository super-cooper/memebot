from typing import Optional

import pymongo as mongo
import pymongo.database

from memebot import config


class DatabaseInternals:
    """
    Class for managing all database internals that do not need to be exposed to the command programmer.
    """

    def __init__(self) -> None:
        self.client: Optional[mongo.MongoClient] = None

    def connect(self) -> None:
        """
        Create a client connection to a MongoDB database
        """
        if self.client is None:
            self.client = mongo.MongoClient(config.database_uri.geturl())

    def get_db(self, db_name: str) -> Optional[mongo.database.Database]:
        if self.client:
            return self.client[db_name]
        return None
