import json
import requests
import os
import re

from bs4 import BeautifulSoup
from time import sleep
from typing import Any, Callable, Tuple, Union
from urllib.parse import urlparse, parse_qs

q = type('Quitter', (), {'__repr__': lambda self: quit()})()

def retry(num_retries=3, delay=1, exceptions=(Exception, requests.RequestException, requests.ConnectionError, requests.Timeout)):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for i in range(num_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(e)
                    sleep(delay)
                print(f'Retrying attempt {i+2}/{num_retries}')
        return wrapper
    return decorator

def write(content: Any, filename: str = 'test.html'):
    with open(filename, 'w', encoding='utf-8') as f:
        if filename.endswith('.json'):
            assert isinstance(content, dict)
            f.write(json.dumps(content, indent=4, ensure_ascii=False))
        elif filename.endswith('html'):
            assert isinstance(content, str)
            soup = BeautifulSoup(content, 'html.parser')
            f.write(soup.prettify())
        else:
            f.write(str(content))

def dfs(data: Union[dict, list], match_fn: Callable[[Any], bool]) -> Tuple[list, list]:
    results = []
    paths = []
    
    def helper(data: Any, path=None):
        if path is None:
            path = []
            
        if match_fn(data):
            results.append(data)
            paths.append(path[:])
            
        if isinstance(data, dict):
            for key, value in data.items():
                helper(value, path + [key])
        elif isinstance(data, list):
            for i, item in enumerate(data):
                helper(item, path + [i])
                
    helper(data)
    return results, paths

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
})
r = s.get('https://courses.erppub.osu.edu/psc/ps/EMPLOYEE/PUB/c/COMMUNITY_ACCESS.OSR_CAT_SRCH.GBL')
soup = BeautifulSoup(r.text, 'html.parser')
courses = soup.find('div', {'id': 'win0divOSR_CAT_SRCH_WK_DESCR'}).find_all('option')
courses = [c.get('value') for c in courses if c.get('value')]
inputs = soup.find_all('input', {'type': 'hidden'})
payload = {i.get('name'): i.get('value') for i in inputs}

START = 1
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ret = []
for i, course in enumerate(courses):
    print(f'Processing {course} ({i+1}/{len(courses)})')
    r = s.post('https://courses.erppub.osu.edu/psc/ps/EMPLOYEE/PUB/c/COMMUNITY_ACCESS.OSR_CAT_SRCH.GBL', data={
        **payload,
        'OSR_CAT_SRCH_WK_DESCR': course,
        'ICAction': 'OSR_CAT_SRCH_WK_BUTTON1',
    })

    soup = BeautifulSoup(r.text, 'html.parser')
    spans = soup.find_all('span', class_='PSQRYTITLE')
    spans = [s.text for s in spans if s.text != 'Catalog Search Results' and s.text != 'Search Criteria']
    print(f'Found {len(spans)} matches for course {course}')
    ret.extend(spans)


    
ret = sorted(list(set(ret)))
ret = [x.split(' - ')[0] for x in ret]

with open(os.path.join(SCRIPT_DIR, 'codes.json'), 'w', encoding='utf-8') as f:
    json.dump(ret, f, indent=4, ensure_ascii=False)



import code; code.interact(local=locals())