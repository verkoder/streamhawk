import requests
from app import jdump


def get_sirius():
    'get all station name IDs via Sirius API'
    response = requests.get('https://xmplaylist.com/api/station')
    if response.status_code == 200:

        # save SiriusXM name & station IDs
        shows = [(x['name'], x['id']) for x in response.json()]
        shows = {k: v for k,v in sorted(shows)}
        jdump(shows, 'sirius')
