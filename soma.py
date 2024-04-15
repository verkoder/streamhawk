import requests
from app import SOMA, jdump


def get_soma():
    'get Soma.fm channel names/ids via API'
    response = requests.get(SOMA)
    if response.status_code == 200:

        # save SomaFM names
        shows = response.json()['channels']
        jdump({x['title']: x['id'] for x in shows}, 'soma')
