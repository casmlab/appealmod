import sys

import pymongo
import logging
from logging import StreamHandler
from datetime import datetime
import json
import pytz
from core.config import Config as config

EST = pytz.timezone('US/Eastern')


# mongoConnectionString = r"mongodb+srv://admin:u8U9VKugQO6EFmrG@cluster0.hxwup.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
mongo_driver = pymongo.MongoClient(config.DB_CONNECTION_STRING)
mongo_database = mongo_driver["main-cluster"]
conversation_logs_collection = mongo_database["conversation-logs"]
application_logs_collection = mongo_database["application-logs"]
user_logs_collection = mongo_database['user-logs']


class MongoDBLogger(StreamHandler):
    def __init__(self):
        super().__init__()

    def emit(self, record):
        try:
            conversation_id = record.conversationID
        except Exception as e:
            conversation_id = None

        msg = self.format(record)
        # write the log message to the mongo database
        application_logs_collection.insert_one({
            "message": msg,
            "timestamp": datetime.now(),
            'conversationID': conversation_id
        })


logging.basicConfig(filename="redditLogging.log", level=logging.INFO,
                    format='%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d:%H:%M:%S')
formatter = logging.Formatter('%(asctime)s,%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                              datefmt='%Y-%m-%d:%H:%M:%S')
mongo_logger = MongoDBLogger()
mongo_logger.setFormatter(formatter)
mongo_logger.setLevel(logging.INFO)
logging.getLogger().addHandler(mongo_logger)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)


class SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        return str(obj)


def sanitize_object_for_mongo(obj):
    return json.loads(json.dumps(vars(obj), cls=SafeJSONEncoder))


def has_conversation_been_logged(praw_conversation):
    return conversation_logs_collection.find_one({"id": praw_conversation.id})


def log_conversation(praw_conversation, bot):
    conversation_data = sanitize_object_for_mongo(praw_conversation)
    message_data = [sanitize_object_for_mongo(m) for m in praw_conversation.messages]
    conversation_id = praw_conversation.id
    to_log = {
        "id": conversation_id,
        "conversationData": conversation_data,
        "messageData": message_data,
    }
    user = praw_conversation.user.name
    ban_info = None
    try:
        ban_info = bot.get_user_ban_information(user)
    except:
        pass
    if ban_info:
        del ban_info['_reddit']
        to_log["banInfo"] = ban_info
    to_log["isBanned"] = "banInfo" in to_log
    existing_conversation = has_conversation_been_logged(praw_conversation)
    if existing_conversation is None:
        to_log["unbannedTime"] = None
        conversation_logs_collection.insert_one(to_log)
        log(f"Logged conversation {conversation_id}")
    else:
        if existing_conversation.get("isBanned") and not to_log.get("isBanned"):
            to_log["unbannedTime"] = datetime.now(EST)
        else:
            to_log["unbannedTime"] = existing_conversation.get("unbannedTime")
        conversation_logs_collection.update_one({"id": conversation_id},
                                                {"$set": to_log})
        log(f"Updated conversation {conversation_id}")


def update_conv_ids(modmail_conversation, user_model):
    # get all conv user has initiated so far -- the main conv id + any other conv ids present
    # check if the current conv is part of it. 
    # if not, then update the user data with a new conv id list which is current list + current conv

    if 'other_conv_ids' in user_model.keys():
        other_conv_ids = user_model['other_conv_ids']
    else:
        other_conv_ids = []

    if modmail_conversation.id == user_model['conv_id'] or modmail_conversation.id in other_conv_ids:  # this is an old conv
        return
    else:
        other_conv_ids.append(modmail_conversation.id)
        username = user_model['username']
        log(f'This is a new conversation by the same user {username}, updating the model with the new conv id',
            conversation_id=modmail_conversation.id)
        update_user_data(modmail_conversation, 'other_conv_ids', other_conv_ids)


def update_user_data(modmail_conversation, key, value, username=None):

    if type(key) is list and type(value) is list:
        pass
    else:
        key = [key]
        value = [value]
    
    if len(key) == len(value):
        update_dict = dict(zip(key, value))
    else:
        log(f'Key and value list size mismatch while updating the user data')
        log(f'Key is {key} and value is {value}')
        update_dict = {}
    
    if username is None:
        username = modmail_conversation.participant.name
    log(f'Updating user DB with dict {update_dict}')
    user_logs_collection.update_one({'username': username}, {'$set': update_dict})


def log_user_data(modmail_conversation, group):
    username = modmail_conversation.participant.name
    sorted_msgs = sorted(modmail_conversation.messages, key=lambda x: x.date)

    appeal_time = sorted_msgs[0].date  ## default time, if no appeal time is found.
    for message in sorted_msgs:
        if message.author.name == username:
            appeal_time = message.date  ## setting the appeal time
            break

    # if getUserGroup(username) is None: # to ensure that we don't create duplicate entries...
    mydict = {
        'username': username,
        'conv_id': modmail_conversation.id,
        'group': group,
        'appeal_time': appeal_time,
        'form_filled': False,
        'form_shared': False,
        'note_shared': False,
        'mod_involved': False,
        'user_deleted': False,
    }
    user_logs_collection.insert_one(mydict)
    log(f'Inserted user {username} to the user DB')
    return mydict


def check_user_model(username):
    mydict = user_logs_collection.find_one({"username": username})
    if mydict:  # user exists already
        log(f'{username} is a repeat user, retrieving previously assigned group')
        return mydict
    else: 
        return None


def log(message, conversation_id=None):
    logging.info(message, extra={'conversationID': conversation_id})
