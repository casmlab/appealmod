# AppealMod
Code for Appealmod bot and its signup website 

## Project structure
### Root folders
- `bot` — our AppealMod bot
- `conf` — configurations common for bot and website (e.g. Slack webhooks)
- `mongo_db` — MongoDB related classes
- `project` — Django project folder (settings, urls, wsgi)
- `static` — Django static folder (img, css, etc.)
- `templates` — Django templates (html)
- `utils` — common useful things both for bot and website
- `web` — Django main app (views, models, etc.)

### Details (TODO)
- **`bot`** — our AppealMod bot
  - `bin` — ...
    - `run_recent_convs.py` — ...
    - `run_started_convs.py` — ...
  - `certs` — ...
    - `config.yaml` — ...
  - `conf` — ...
    - `conf.py` — ...
  - `src` — ...
    - `logger` — ...
      - `L.py` — ...
      - `logger.py` — ...
      - `mongo_handler.py` — ...
    - `runners` — ...
      - `recent_convs.py` — ...
      - `started_convs.py` — ...
    - `dialogue_bot` — ...
    - `form.py` — ...
    - `reddit_bot.py` — ...
    - `trigger.py` — ...
  - `tests` — ...
    - `testing_script.py` — ...
  - `config.py` — ...
- `conf` — configurations common for bot and website (e.g. Slack webhooks)
  - `conf.py` — ...
  - `local_conf.py` — ...
- `mongo_db` — MongoDB related classes
  - `utils` — ...
    - `sanitizer.py` — ...
  - `db.py` — ...
  - `db_bot_responses.py` — ...
  - `db_conversations.py` — ...
  - `db_logs.py` — ...
  - `db_subreddits.py` — ...
  - `db_users.py` — ...
- `project` — Django project folder (settings, urls, wsgi)
  - `asgi.py` — ...
  - `settings.py` — ...
  - `local_settings.py` — ...
  - `urls.py` — ...
  - `wsgi.py` — ...
- `static` — Django static folder (img, css, etc.)
  - `css` — ...
  - `img` — ...
- `templates` — Django templates (html)
- `utils` — common useful things both for bot and website
  - `slack` — currently only Slack utils so far
    - `decorator.py` — ...
    - `exceptions.py` — ...
    - `styling.py` — ...
    - `webhooks.py` — ...
- `web` — Django main app (views, models, etc.)
  - `migrations` — ...
  - `views` — ...
    - `api` — ...
      - `db` — ...
        - ...
      - `api_form.py` — ...
    - `debug.py` — ...
    - `form.py` — ...
    - `home.py` — ...
  - `admin.py` — ...
  - `apps.py` — ...
  - `forms.py` — ...
  - `models.py` — ...
  - `tests.py` — ...
- `Dockerfile` — ...
- `manage.py` — ...
- `README.md` — ...
- `requirements.txt` — ...
- `run.sh` — ...

## Logging 

We log data to the following destinations:
* MongoDB (the `application-logs` collection)
* A local file (`redditLogging.log`)
* The console
* Slack channels

### Slack channels

We use CSMR Slack workspace and have the following Slack channels there: 

- **#ap-main** — the main channel for important status messages only
  - TODO: _configuration not yet finished_
- **#ap-steps** — updates on conversations being processed and their key steps 
- **#ap-errors** — unexpected exceptions and various error cases
- **#ap-alerts** — TBD, used for tracking rare but important events that are less critical than errors
  - also includes exceptions that do not stop jobs

Additionally, we have one Slack channel in the hidden CSMR (logging) workspace:

- **#ap-logging** — all logging messages
  - TODO: _not all logging is configured here yet_

## Prod Instance

### Deployment to Production 

There are two ways to deploy:
* Automatic: Push changes to the `main` branch that will trigger automated deployment
* Manual: Run the script `restart_appealmod.sh` located in the root directory of our VM to run the deployment steps manually

If something goes wrong during the deployment process, check the logfile at `/tmp/appealmod_build.log` 

### Secrets in Production

The secrets are stored here:
* `/home/appealmod/appealmod/bot/certs/config.yaml`

### Adding or Removing Subreddits in Production

To add or remove subreddits, modify the Python list in: 
* `/home/appealmod/appealmod/bot/conf/conf.py`

Then redeploy.

## Local Instance

### Setting up a Local Instance

#### 1. Pull the latest version from the `main` branch

#### 2. Set the required values in `/bot/certs/config.yaml`

* `reddit_email` — _probably never used_
* Authentication our bot on the Reddit API:
  * `reddit_username`
  * `reddit_password`
  * `client_id`
  * `client_secret`
  * `user_agent`
* `db_connection_string` — MongoDB connection string
* `debug`:
  * `true` — to avoid the bot applying actions on Reddit
  * `false` — to allow the bot to apply actions on Reddit
* `treatment_fraction`:
  * `1` — if the "control group" mechanism is not being used
  * `0.5` — for a 50% "control group"
* `dialogue_update_interval` — how often “already started conversations” are processed
* `update_cutoff` — the maximum age of a conversation (in days) that can still be processed before it’s ignored due to being too old

#### 3. Run the bot script

We have options for running the bot:

1. Run it via Docker
2. Run it manually (using virtualenv and pip)

Steps for manual execution:

1. Сreate a virtual environment and activate it:
   * `python3 -m venv venv`
   * `source venv/bin/activate`
   * Note: we are using Python 3.10
2. Run `pip install -r requirements.txt`  
3. Either run `run.sh` script or run the specific files manually:
   * `bot/bin/run_recent_convs.py` 
     * (for process recently created conversations)
   * `bot/bin/run_started_convs.py`
     * (for process already created conversations)
4. Run `python3 manage.py runserver` to start the Django website

### Testing Script 
  
We have an automated script located at `bot/tests/testing_script.py`, 
but it is not fully completed yet.

The current steps performed by the script are:

1. Authenticate via an additional Reddit API (with admin access, but not using our bot)
   * Unban the testing user
   * Ban the testing user
2. Authenticate as the testing user
   * Retrieve the user's inbox messages
   * Find and reply to the "permanently banned" message
3. Wait for our bot to process the ban appeal:
   * by checking if relevant entry is created in MongoDB

**Better manual testing steps are** 
_(to be implemented in automated script later):_
1. Clean up any previous data related to the testing user (if it was processed before):
   * Remove the user from MongoDB
   * Remove the user's form entry from PostgresDB
   * Authenticate as our bot and archive all conversations involving the testing user 
2. Ensure the testing user has made a contribution to the testing subreddit
3. Ban testing user (including a note/reason for the ban) -- you will need a second bot acount for this. 
4. The testing user should reply to the "permanently banned" message
5. Verify the bot processed the appeal correctly:
   * The user's entry was created in MongoDB
   * A form entry was created in PostgresDB
   * The bot sent and initial message to the testing user
   * The bot archived the conversation
6. The testing user should complete the form
7. Verify the bot processed the form submission correctly:
   * The bot replied to the user
   * The bot sent a message to the moderators (including the user's form responses)
   * The bot unarchived the conversation

For internal details on testing bots and subreddits, refer to this [link](https://docs.google.com/document/d/1Igjv3xUr1YVvtDiGQOg-1Ox0IdU5c9zJc-FgGSHPZvs/edit)
