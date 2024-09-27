slack_disabled = False

slack_hook_steps = None  # should be set in `local_conf.py`
slack_hook_status = None  # should be set in `local_conf.py`
slack_hook_alerts = None  # should be set in `local_conf.py`
slack_hook_errors = None  # should be set in `local_conf.py`
slack_hook_logging = None

try:
    from .local_conf import *
except ImportError:
    pass
