import json
import requests
import os
import re

from bs4 import BeautifulSoup
from time import sleep
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

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
})

# https://catalog.ufl.edu/UGRD/courses/
# https://gradcatalog.ufl.edu/graduate/courses-az/

links = [
    {
        'name': 'Graduate Courses',
        'url': 'https://gradcatalog.ufl.edu/graduate/courses-az/',
        'course_pattern': r'^/graduate/courses-az/[a-zA-Z]+'
    },
    {
        'name': 'Undergraduate Courses',
        'url': 'https://catalog.ufl.edu/UGRD/courses/',
        'course_pattern': r'^/UGRD/courses/[a-zA-Z]+'
    },
]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

ret = []
for link in links:
    r = s.get(link['url'])
    soup = BeautifulSoup(r.text, 'html.parser')
    hrefs = [a.get('href') for a in soup.find_all('a', href=re.compile(link['course_pattern']))]
    hrefs = sorted(list(set(hrefs)))
    for i, href in enumerate(hrefs):
        print(f'{link["name"]} {i+1}/{len(hrefs)}: {href}')
        base = urlparse(link['url']).scheme + '://' + urlparse(link['url']).netloc
        r = retry()(s.get)(f'{base}{href}')
        soup = BeautifulSoup(r.text, 'html.parser')
        course_blocks = soup.find_all('p', class_='courseblocktitle')
        codes = [' '.join(block.text.strip().replace('\xa0', ' ').split()[:2]) for block in course_blocks]
        ret.extend(codes)

ret = sorted(list(set(ret)))   

with open(os.path.join(SCRIPT_DIR, 'codes.json'), 'w', encoding='utf-8') as f:
    json.dump(ret, f, indent=4, ensure_ascii=False)


import code; code.interact(local=locals())