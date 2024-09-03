import os
import json


class QualtricsMap(object):
    """Stores all the mapping info related to qualtrics questions"""

    def __init__(self):
        super().__init__()

    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, '..', 'qualtrics-dictionary.json')

    with open(filename) as input_file:
        dicts = json.load(input_file)

    QID_LIST = [x['question_id'] for x in dicts]
    DICTIONARY = dicts
