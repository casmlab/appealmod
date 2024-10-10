from bot.conf import conf


class DbUsers:
    def __init__(self, collection):
        self.collection = collection

    def get(self, username, subreddit):
        return self.collection.find_one({"username": username,
                                         "subreddit": subreddit})

    def all(self):
        return self.collection.find({'subreddit': {'$in': conf.subreddits_ids}},
                                    batch_size=30)

    def update_conv_ids(self, conv, user):
        ...

    def update(self, conv, key, value):
        ...

    def get_or_create(self, conv):
        ...

    def add(self, conv, group):
        ...
