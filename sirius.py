import requests
from loader import SIRIUS, jdump


def get_sirius():
    'download SiriusXM stream names & IDs'
    response = requests.get(SIRIUS)
    if response.status_code == 200:

        shows = [(x['name'], x['id']) for x in response.json()]
        shows.sort(key=lambda x: x[0].lower())
        jdump(dict(shows), 'sirius')
