from numpy.random import binomial

from bot.conf import conf
from bot.config import Config as config
from bot.src.logger.L import L


class DbUsers:
    def __init__(self, collection):
        self.collection = collection

    def get(self, username, subreddit):
        return self.collection.find_one({"username": username,
                                         "subreddit": subreddit})

    def all(self):  # todo: rename this method? (because not all anymore)
        return self.collection.find({
            'subreddit': {'$in': conf.subreddits_ids},
            'group': 1,
            'ignored': False,
            'user_deleted': False,
        }, batch_size=30)

    def update_conv_ids(self, conv, user):
        """
        Get all conv user has initiated so far -- the main conv id + any other conv ids present
        check if the current conv is part of it.
        if not, then update the user data with a new conv id list which is current list + current conv
        """
        other_conv_ids = user.get('other_conv_ids', [])

        if conv.id == user['conv_id'] or conv.id in other_conv_ids:  # this is an old conv
            return

        other_conv_ids.append(conv.id)
        self.update(conv, 'other_conv_ids', other_conv_ids)

    def update(self, conv, key, value, force_username=None):
        username = force_username if force_username else conv.participant.name
        subreddit = str(conv.owner)

        update = {key: value}

        L.logging(f"User `{username}`: Updating data {update}")
        self.collection.update_one({'username': username, 'subreddit': subreddit},
                                   {'$set': update})

    def get_or_create(self, conv, treatment_fraction=config.TREATMENT_FRACTION):
        username = conv.participant.name
        subreddit = str(conv.owner)

        user = self.get(username, subreddit)
        if user:  # this is repeat user
            # update conv ids if this is a new conversation
            self.update_conv_ids(conv, user)
            return user, False

        else:
            # assign a new random group. 1 denotes treatment. 0 denotes control
            group = binomial(1, treatment_fraction)
            user = self.add(conv, group)  # we log user data here
            return user, True

    def add(self, conv, group):
        username = conv.participant.name
        subreddit = str(conv.owner)

        # Get `appeal_time` value:
        sorted_msgs = sorted(conv.messages, key=lambda x: x.date)
        appeal_time = sorted_msgs[0].date  # default, if no `appeal_time` found
        for message in sorted_msgs:
            if message.author.name == username:
                appeal_time = message.date  # set `appeal_time`
                break

        user = {
            'username': username,
            'conv_id': conv.id,
            'subreddit': subreddit,
            'group': group,
            'appeal_time': appeal_time,
            'form_filled': False,
            'form_shared': False,
            'note_shared': False,
            'mod_involved': False,
            'user_deleted': False,
            'ignored': False,
        }
        self.collection.insert_one(user)
        return user
