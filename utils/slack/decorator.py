from bot.src.logger.L import L


def slack(name):
    def decorator(func):

        def wrapped(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                L.exception(e, only_alert=False)
                raise
            return result

        return wrapped
    return decorator
