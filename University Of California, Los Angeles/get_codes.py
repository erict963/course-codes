import json
import requests
import os
import re

from bs4 import BeautifulSoup
from time import sleep
from typing import Any, Callable, Tuple, Union
from urllib.parse import urlparse, parse_qs

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

PAGE_SIZE = 50
TOTAL = 1000000 # a large number to ensure we get all results
# r = s.post(
#     'https://api-us-west-1.prod.courseloop.com/publisher/search-academic-items',
#     data=json.dumps({
#         "siteId": "ucla-prod-pres",
#         "query": "",
#         "contenttype": "subject",
#         "searchFilters": [
#             {
#                 "filterField": "implementationYear",
#                 "filterValue": ["2025"],
#                 "isExactMatch": False
#             },
#             {
#                 "filterField": "active",
#                 "filterValue": ["1"],
#                 "isExactMatch": False
#             }
#         ],
#         "from": TOTAL,
#         "size": PAGE_SIZE
#     })
# )
# print(json.dumps(r.json(), indent=4, ensure_ascii=False))
ret = []
for offset in range(0, TOTAL, PAGE_SIZE):
    r = s.post(
        'https://api-us-west-1.prod.courseloop.com/publisher/search-academic-items',
        data=json.dumps({
            "siteId": "ucla-prod-pres",
            "query": "",
            "contenttype": "subject",
            "searchFilters": [
                {
                    "filterField": "implementationYear",
                    "filterValue": ["2025"],
                    "isExactMatch": False
                },
                {
                    "filterField": "active",
                    "filterValue": ["1"],
                    "isExactMatch": False
                }
            ],
            "from": offset,
            "size": PAGE_SIZE
        })
    )
    if r.status_code != 200:
        print('Failed to fetch data, status code:', r.status_code)
        break
    if not r.json().get('data', {}).get('results', []):
        print('No more data to fetch, stopping.')
        break
    data = r.json().get('data', {}).get('results', [])
    codes = [item['code'] for item in data if 'code' in item]
    ret.extend(codes)
    print('Codes: ', codes[:5])
    print(f'Fetched {len(codes)} codes, total so far: {len(ret)}')

ret = [re.sub(r'[\-]', ' ', x) for x in ret]
ret = sorted(list(set(ret)))

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(SCRIPT_DIR, 'codes.json'), 'w', encoding='utf-8') as f:
    json.dump(ret, f, indent=4, ensure_ascii=False)

print(f'Saved {len(ret)} codes to codes.json')