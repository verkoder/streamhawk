'''crawler.py -- get current Soma logos, PRE-PROCESS ONLY: not used in app
tk uses only gif w/o PIL (which crashes py2app)
- download 256x256 Soma logos
- resize to 165x165
- convert from png/jpg to gif
- save to logos folder'''
import os
import requests
from time import sleep
from PIL import Image

from loader import jload

SOMA_LOGOS = 'https://somafm.com/logos/256/'
LOGO_FOLDER = './logos/'


def get_logos():
    'download/resize/gif current Soma logos'
    done = 0
    soma = jload('soma').values()
    print(f'{len(soma)} SOMA LOGOS...')
    for chan in soma:
        urls = [f'{SOMA_LOGOS}{chan}256.png', # most to least likely names
                f'{SOMA_LOGOS}{chan}256.jpg',
                f'{SOMA_LOGOS}{chan}-256.jpg']
        while urls:
            sleep(0.3)
            url = urls.pop(0)
            response = requests.get(url)
            if response.status_code == 200:
                break
        else:
            print(chan, '• 404 IMAGE NOT FOUND')
            continue
        tmp = f'_tmp.{url[-3:]}'
        with open(tmp, 'wb') as f: # cache jpg/png
            f.write(response.content)
        with Image.open(tmp) as img: # read cache
            img.thumbnail((165, 165)) # resize
            img.save(f'{LOGO_FOLDER}{chan}.gif') # make gif
        print(chan, '• OK')
        os.remove(tmp)
        done += 1
    print(f'{done} DOWNLOADED')
