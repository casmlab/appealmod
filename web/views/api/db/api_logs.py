from datetime import datetime

from rest_framework.response import Response
from rest_framework.views import APIView

from mongo_db.db import db


class DbLogsApiView(APIView):
    def post(self, request, *args, **kwargs):
        message = request.data.get('message')
        subreddit = request.data.get('subreddit')
        conv_id = request.data.get('conversationID')

        db.logs.insert_one({
            "message": message,
            "timestamp": datetime.now(),
            'conversationID': conv_id,
            'subreddit': subreddit,
        })

        return Response({
            'success': True,
        })
