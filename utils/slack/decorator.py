from utils.slack.exceptions import slack_exception


def slack(name):
    def decorator(func):

        def wrapped(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                slack_exception(name, e)
                raise
            return result

        return wrapped
    return decorator
