import re
import requests
from StreamHawk import jdump

URL = 'https://somafm.com/'
SOMA = re.compile(r'(?is)<li class="cbshort">\s*<a href="/(.*?)/".*?<h3>(.*?)</h3>')


def get_soma():
    'get all SomaFM names & playlist URLs via web'
    response = requests.get(URL)
    if response.status_code == 200:

        # save SomaFM names & URLs
        html = response.content.decode('utf-8')
        shows = [(x.group(2), f'{URL}{x.group(1)}/') for x in SOMA.finditer(html)]
        shows = {k: v for k,v in sorted(shows)}
        jdump(shows, 'soma')
