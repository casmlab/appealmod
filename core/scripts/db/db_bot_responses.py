

class DbBotResponses:
    def __init__(self, collection):
        self.bot_responses = collection

    def get(self, subreddit):
        # fixme: temp version: cursor = self.responses.find(); list(cursor)[0]
        return self.bot_responses.find_one({'subreddit': subreddit})
