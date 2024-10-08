from rest_framework.views import APIView
from rest_framework.response import Response

from web.models import BanAppealData


class FormApiView(APIView):
    def get(self, request, *args, **kwargs):
        username = request.GET.get('username')
        subreddit = request.GET.get('subreddit')

        print(username, subreddit)
        obj = BanAppealData.objects.auth(username, subreddit)
        print(obj)

        return Response({
            'success': obj is not None,
        })

    def post(self, request, *args, **kwargs):
        username = request.GET.get('username')
        subreddit = request.GET.get('subreddit')

        obj = BanAppealData.objects.create(username, subreddit)

        if obj is None:
            return Response({
                'success': False,
            })

        return Response({
            'success': True,
            'filled':  obj.filled(),
            'data': obj.to_json(),
        })
