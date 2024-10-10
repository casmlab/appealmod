import pytz
from rest_framework.views import APIView

from mongo_db.db import db

EST = pytz.timezone('US/Eastern')


class DbConversationsApiView(APIView):
    def get(self, request, *args, **kwargs):
        """ Has conversation been logged? """
        conv_id = request.GET.get('id')
        return db.conversations.find(conv_id)

    def post(self, request, *args, **kwargs):
        # add(conv)
        ...
