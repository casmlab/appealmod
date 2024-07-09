import requests, json
from core.config import Config as config
from core.scripts.redditLogging import log
from core.scripts.qualtricsMap import QualtricsMap as qm
import traceback
from urllib.parse import urlparse, parse_qs


def is_extra_text(key):
    return len(key.split('_')) > 2


def parse_qualtrics_response(response):
    # question_types = {
    # 	"QID8": "comment_labeling",
    # 	"QID2": "aware_reason",
    # 	"QID3": "explain_rule",
    # 	"QID5": "explain_behavior",
    # 	"QID6": "behavior_wrong",
    # 	"QID7": "pledge",
    # 	"QID10": "appeal_reason",
    # 	"QID11": "pledge_reflection"
    # }

    question_types = qm.QID_LIST
    result = {}

    extra_text = {}

    for key in response["values"]:
        for qType in question_types:
            if key.startswith(qType):
                result[qType] = response["values"][key]
                if is_extra_text(key):
                    extra_text[qType] = response['values'][key]

    for key in response["labels"]:
        for qType in question_types:
            if key.startswith(qType):
                result[qType] = response["labels"][key]

    # replacing fixed fields with user-provided text (in case the user chooses the "other" option)
    for key in extra_text:
        result[key] = extra_text[key]

    return result


def update_contacts_list(reddit_username):

    log(f"Checking if the contact {reddit_username} already exists")
    if does_contact_exist(reddit_username):
        return None

    log(f"Contact {reddit_username} does not exist")
    contacts_endpoint = "/v3/mailinglists/" + config.QUALTRICS_CONTACT_LIST_ID + "/contacts"
    headers = {'X-API-TOKEN': config.QUALTRICS_TOKEN}

    body = {
        "firstName": "default",
        "email": "default@gmail.com",
        "embeddedData": {
            "reddit-username": reddit_username,
        },
        "externalDataRef": reddit_username,
        "unsubscribed": False
    }

    url = config.QUALTRICS_BASE_URL + contacts_endpoint
    # no write operations in debug mode.
    if not config.DEBUG:
        r = requests.post(url, json=body, headers=headers)
        if r.status_code == requests.codes.ok:
            log(f"Successfully added the contact {reddit_username} to qualtrics contacts list")
        else:
            log(f"Some error in updating the contact list with {reddit_username}")
            log(r.text)


def does_contact_exist(reddit_username):
    contact_list, next_page = get_contact_list()
    j = 0

    while True:
        if contact_list is not None:
            for contact in contact_list:
                if contact['embeddedData']['reddit-username'] == reddit_username:
                    log(f"Contact {reddit_username} already exists")
                    return True
        if next_page is not None:
            j += 1
            skip_token = parse_qs(urlparse(next_page).query)['skipToken'][0]
            contact_list, next_page = get_contact_list(skip_token)
        else:
            break
    return False


def get_contact_list(skip=None):
    contacts_endpoint = "/v3/mailinglists/" + config.QUALTRICS_CONTACT_LIST_ID + "/contacts"
    headers = {'X-API-TOKEN': config.QUALTRICS_TOKEN}
    payload = {'skipToken': skip}

    url = config.QUALTRICS_BASE_URL + contacts_endpoint
    if skip is not None:
        r = requests.get(url, headers=headers, params=payload)
    else:
        r = requests.get(url, headers=headers)
    if r.status_code == requests.codes.ok:
        log(f"Retrieved the contact list")
        output = r.json()
        next_page = output['result']['nextPage']
        contact_list = output['result']['elements']
        # print(output)
        return contact_list, next_page
    else:
        log(f"Trouble retrieving contact list")
        log(r.text)
        return None, None


def get_survey_response(reddit_username, start_time, parse=True):
    export_endpoint = "/v3/surveys/" + config.QUALTRICS_SURVEY_ID + "/export-responses/"
    headers = {'X-API-TOKEN': config.QUALTRICS_TOKEN}
    url = config.QUALTRICS_BASE_URL + export_endpoint
    if start_time is not None:
        body = {
            "format": 'json',
            'compress': False,
            'startDate': start_time
        }
    else:
        body = {
            "format": 'json',
            'compress': False,
        }

    log(f"Exporting survey responses for user {reddit_username}")

    r = requests.post(url, json=body, headers=headers)

    if r.status_code == requests.codes.ok:
        log(f"Successfully created the export request")
        # print(r.text)

        file_id = get_file_id(r, url, headers)
        if file_id is not None:
            log(f"Received the id for the export file {file_id}")
            file_url = url + file_id + '/file'
            file_r = requests.get(file_url, headers=headers, stream=True)
            responses = file_r.json()['responses']
            log(f"Retrieved {len(responses)} from qualtrics")
            for response in responses:
                try:
                    status = response['values']['status']
                    if not status == 0:
                        log(f"Found an invalid response with status {status}, will be ignored")
                        continue

                    surveyor = response['values']['reddit-username']
                    if surveyor == reddit_username:
                        log(f'Found the survey response for user {reddit_username}')
                        if not response['values']['finished'] == 1:
                            log(f"Found an incomplete response from user {reddit_username}, will be ignored")
                            return {}
                        if parse:
                            return parse_qualtrics_response(response)
                        else:
                            return response

                except Exception as e:
                    error_message = traceback.format_exc()
                    log(f'Exception in reading survey responses {e}')
                    log(error_message)

            log(f'Did not find any response from the user {reddit_username}')
            return {}
        # with open('survey-response.json','w') as outputfile:
        # 	json.dump(file_r.json(), outputfile)
        # 	# this will be the main return function
        else:
            log(f"Did not receive a valid file ID")
            return None
    else:
        log(f"Failed to create the export request")
        log(r.text)
        return None


def get_file_id(r, url, headers):
    progress = r.json()['result']['percentComplete']
    progress_id = r.json()["result"]["progressId"]
    status = r.json()['result']['status']
    log(f"Export progress status: {status}")

    while status != "complete" and status != "failed":
        status_url = url + progress_id
        status_r = requests.get(status_url, headers=headers)

        if r.status_code == requests.codes.ok:
            progress = status_r.json()["result"]["percentComplete"]
            log(f"Download is {progress} complete")
            status = status_r.json()["result"]["status"]

    # hopefully it should never come to an else condition here

    if status == "failed":
        log(f"Export failed")
        log(status_r.text())
        return None

    return status_r.json()["result"]["fileId"]


def parse_survey_response():
    pass
