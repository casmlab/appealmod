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
    REDDIT_EMAIL = config['reddit_email']
    REDDIT_USERNAME = config['reddit_username']
    REDDIT_PASSWORD = config['reddit_password']
    USER_AGENT = config['user_agent']
    CLIENT_ID = config['client_id']
    CLIENT_SECRET = config['client_secret']
    
    # Credentials for Database connection
    # DB_USERNAME = config['db_username']
    # DB_PASSWORD = config['db_password']
    DB_CONNECTION_STRING = config['db_connection_string']

    DEBUG = bool(config['debug'])
    TREATMENT_FRACTION = config['treatment_fraction'] 

    DIALOGUE_UPDATE_INTERVAL = int(config['dialogue_update_interval'])
    UPDATE_CUTOFF = int(config['update_cutoff'])
    # credentials for Qualtrics
    QUALTRICS_TOKEN = config['qualtrics_token']
    QUALTRICS_BASE_URL = config['qualtrics_base_url']
    QUALTRICS_CONTACT_LIST_ID = config['qualtrics_contact_list_id']
    QUALTRICS_SURVEY_ID = config['qualtrics_survey_id']
