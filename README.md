# appealmod
Code for Appealmod bot and its signup website 

## We’ll have such a project structure now:
bot — our AppealMod bot
conf — configurations common for bot and website (e.g. Slack webhooks)
mongo_db — MongoDB related classes
project — Django project folder (settings, urls, wsgi)
static — Django static folder (img, css, etc.)
templates — Django templates (html)
utils — common useful things both for bot and website (currently only Slack utils so far)
web — Django main app (views, models, etc.)

## Logging (via slack channel)

Errors and logs will be tracked in the CSMR Slack workspace. Following are the slack channels:

ap-status — the main channel with all current job statuses (which conversations are processing and those short results)
ap-errors — unexpected exceptions and various error cases
ap-alerts — tbd, some rare important things to track, but not so critical like errors
ap-logging - complete logging
