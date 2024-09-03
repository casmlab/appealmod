from pymongo import MongoClient

from core.config import Config as config
from core.scripts.db.db_bot_responses import DbBotResponses


class Database:
    def __init__(self):
        client = MongoClient(config.DB_CONNECTION_STRING)
        cluster = client['main-cluster']

        self.bot_responses = DbBotResponses(cluster['bot-responses'])


db = Database()
