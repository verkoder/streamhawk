import json
from tkinter import messagebox

SITES = {'soma': 'Soma.fm',
         'sirius': 'SiriusXM'}
SOMA = 'http://api.somafm.com/channels.json'
SIRIUS = 'https://xmplaylist.com/api/station'


def hawk_error(msg):
    messagebox.showerror('StreamHawk Error', msg)

def jload(name):
    try:
        with open(f'{name}.json') as f:
            return json.load(f)
    except FileNotFoundError:
        data = [] if name in ('artists', 'streams') else {}
        json.dump(data, open(f'{name}.json', 'w'), indent=4)
        return data
    except json.JSONDecodeError as err:
        hawk_error(f'Error in "{name}.json" file:\n{err}')

def jdump(data, name):
    try:
        with open(f'{name}.json', 'w') as f:
            json.dump(data, f, indent=4)
    except FileNotFoundError:
        hawk_error(f'Missing file: "{name}.json"')
