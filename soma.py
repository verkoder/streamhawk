import requests
from loader import SOMA, jdump


def get_soma():
    'download Soma.fm stream names & IDs'
    response = requests.get(SOMA)
    if response.status_code == 200:

        shows = [(x['title'], x['id']) for x in response.json()['channels']]
        shows.sort(key=lambda x: x[0].lower())
        jdump(dict(shows), 'soma')
