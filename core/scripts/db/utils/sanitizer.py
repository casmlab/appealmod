import json


class SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        return str(obj)


def sanitize(obj):
    """
    Sanitizes object for mongo.
    """
    return json.loads(json.dumps(vars(obj), cls=SafeJSONEncoder))
