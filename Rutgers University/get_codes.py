import json
import requests
import os
import re

from bs4 import BeautifulSoup
from time import sleep
from typing import Any, Callable, Tuple, Union
from urllib.parse import urlparse, parse_qs

q = type('Quitter', (), {'__repr__': lambda self: quit()})()

def retry(num_retries=3, delay=1, exceptions=(Exception,)):
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

# https://classes.rutgers.edu/soc/

SEMESTERS = [
    '92025', # fall 2025
    '02026', # winter 2026
    '12026', # spring 2026
]
CAMPUSES = ['NB', 'NK', 'CM', 'ONLINE_NB', 'ONLINE_NK', 'ONLINE_CM', 'B', 'CC', 'H', 'CU', 'MC', 'WM', 'L', 'AC', 'J', 'D', 'RV']
LEVEL = 'U,G'

from itertools import product
iterator = list(product(SEMESTERS, CAMPUSES))
ret = {}
for i, (semester, campus) in enumerate(iterator):
    r = s.get('https://classes.rutgers.edu/soc/api/courses.json',
                params = {
                    'year': semester[1:],
                    'term': semester[0],
                    'campus': campus,
                }
    )
    courses = r.json()
    print(f'Fetched semester {semester} campus {campus} ({i+1}/{len(iterator)}): {len(courses)} courses')
    for x in courses:
        ret[x['courseString']] = ret.get(x['courseString'], []) + [{'semester': semester, 'title': x['title']}]

# f'{x["offeringUnitCode"]}:{x["subject"]}:{x["courseNumber"]} {x["title"]}' for x in courses
# used to be this^
ret = [f'{k} {v[0]["title"]}' for k, v in ret.items()]
ret = [re.sub(r'[\-]', ' ', x) for x in ret]
ret = [re.sub(r'["\'().,+/?@]', '', x) for x in ret]
ret = sorted(list(set(ret)))

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(SCRIPT_DIR, 'codes.json'), 'w', encoding='utf-8') as f:
    json.dump(ret, f, indent=4, ensure_ascii=False)

