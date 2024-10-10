
from rest_framework.views import APIView

from mongo_db.db import db


class DbBotResponsesApiView(APIView):
    def get(self, request, *args, **kwargs):
        subreddit = request.GET.get('subreddit')
        return db.bot_responses.get(subreddit)
