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

# https://bulletins.psu.edu/university-course-descriptions/undergraduate/
# https://bulletins.psu.edu/university-course-descriptions/graduate/

START = 1
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

ret = []
for level in ['undergraduate', 'graduate']:
    r = s.get(f'https://bulletins.psu.edu/university-course-descriptions/{level}/')
    soup = BeautifulSoup(r.text, 'html.parser')
    links = soup.find_all('a', href=re.compile(r'^/university-course-descriptions'))

    urls = [
        f'https://bulletins.psu.edu{link["href"]}' for link in links
        if link['href'].startswith(f'/university-course-descriptions/{level}/') and 'pdf' not in link['href']
    ]

    for i, url in enumerate(urls):
        if i < START - 1:
            print(f'Skipping URL {i+1}/{len(urls)}: {url}')
            continue
        print(f'**** Processing URL {i+1}/{len(urls)}: {url} ***')
        # r = s.get(url)
        r = retry()(s.get)(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        codes = soup.find_all('div', class_='course_code')
        codes = [code.text.replace('\n', ' ').strip() for code in codes]
        ret.extend(codes)

        with open(os.path.join(SCRIPT_DIR, 'codes.json'), 'w', encoding='utf-8') as f:
            json.dump(ret, f, indent=4, ensure_ascii=False)

ret = sorted(list(set(ret)))
ret = [re.sub(r'[-_]', '', x) for x in ret] # sub dashes and underscores with nothing

with open(os.path.join(SCRIPT_DIR, 'codes.json'), 'w', encoding='utf-8') as f:
    json.dump(ret, f, indent=4, ensure_ascii=False)



import code; code.interact(local=locals())