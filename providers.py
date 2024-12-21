import requests
from loader import SIRIUS, SOMA, jdump


def get_sirius():
    'download SiriusXM stream name/ID list'
    response = requests.get(SIRIUS)
    if response.status_code == 200:

        shows = [(x['name'], x['id']) for x in response.json()]
        shows.sort(key=lambda x: x[0].lower())
        jdump(dict(shows), 'sirius')

def get_soma():
    'download Soma.fm stream name/ID list'
    response = requests.get(SOMA)
    if response.status_code == 200:

        shows = [(x['title'], x['id']) for x in response.json()['channels']]
        shows.sort(key=lambda x: x[0].lower())
        jdump(dict(shows), 'soma')
