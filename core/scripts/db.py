from pymongo import MongoClient

from core.config import Config as config


class Database:
    def __init__(self):
        cluster = MongoClient(config.DB_CONNECTION_STRING)
        self.database = cluster['main-cluster']
        self.responses = self.database['bot-responses']

    def get_responses(self, subreddit):
        cursor = self.responses.find({'subreddit': subreddit})
        output = list(cursor)[0]
        return output
