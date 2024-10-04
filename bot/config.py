import yaml
import os


class Config(object):
    """
    Base configuration
    -load Reddit account information
    -load Database credentials
    """

    def __init__(self):
        super().__init__()

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'certs/config.yaml')

    with open(filename)as y:
        config = yaml.load(y, Loader=yaml.FullLoader)
    
    # Credentials for Reddit user account
    BOT_EMAIL = config['bot_email']
    BOT_USERNAME = config['bot_username']
    BOT_PASSWORD = config['bot_password']
    BOT_USER_AGENT = config['bot_user_agent']
    BOT_CLIENT_ID = config['bot_client_id']
    BOT_CLIENT_SECRET = config['bot_client_secret']
    
    # Credentials for Test Admin Reddit user account
    TEST_ADMIN_USERNAME = config['test_admin_username']
    TEST_ADMIN_PASSWORD = config['test_admin_password']
    TEST_ADMIN_USER_AGENT = config['test_admin_user_agent']
    TEST_ADMIN_CLIENT_ID = config['test_admin_client_id']
    TEST_ADMIN_CLIENT_SECRET = config['test_admin_client_secret']

    # Credentials for Test User Reddit user account
    TEST_USER_USERNAME = config['test_user_username']
    TEST_USER_PASSWORD = config['test_user_password']
    TEST_USER_USER_AGENT = config['test_user_user_agent']
    TEST_USER_CLIENT_ID = config['test_user_client_id']
    TEST_USER_CLIENT_SECRET = config['test_user_client_secret']

    # Credentials for Database connection
    # DB_USERNAME = config['db_username']
    # DB_PASSWORD = config['db_password']
    DB_CONNECTION_STRING = config['db_connection_string']

    DEBUG = bool(config['debug'])
    TREATMENT_FRACTION = config['treatment_fraction'] 

    DIALOGUE_UPDATE_INTERVAL = int(config['dialogue_update_interval'])
    UPDATE_CUTOFF = int(config['update_cutoff'])
