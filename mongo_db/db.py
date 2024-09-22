from pymongo import MongoClient

from core.config import Config as config
from mongo_db.db_bot_responses import DbBotResponses
from mongo_db.db_conversations import DbConversations
from mongo_db.db_logs import DbLogs
from mongo_db.db_subreddits import DbSubreddits
from mongo_db.db_users import DbUsers


class Database:
    def __init__(self):
        client = MongoClient(config.DB_CONNECTION_STRING)
        cluster = client['main-cluster']

        self.bot_responses = DbBotResponses(cluster['bot-responses'])
        self.conversations = DbConversations(cluster['conversation-logs'])
        self.logs = DbLogs(cluster['application-logs'])
        self.subreddits = DbSubreddits(cluster['subreddits_info'])  # fixme: never used?
        self.users = DbUsers(cluster['user-logs'])


db = Database()
