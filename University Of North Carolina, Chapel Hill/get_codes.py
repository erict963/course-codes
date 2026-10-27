import json
import requests
import os
import re

from bs4 import BeautifulSoup
from time import sleep

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

# https://catalog.unc.edu/courses/
BASE_URL = 'https://catalog.unc.edu'
COURSES_URL = f'{BASE_URL}/courses/'
SUBJECT_PATTERN = re.compile(r'^/courses/[a-zA-Z]+/$')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

r = retry()(s.get)(COURSES_URL)
soup = BeautifulSoup(r.text, 'html.parser')
hrefs = sorted(set(a.get('href') for a in soup.find_all('a', href=SUBJECT_PATTERN)))

ret = []
for i, href in enumerate(hrefs):
    print(f'Subject {i+1}/{len(hrefs)}: {href}')
    r = retry()(s.get)(f'{BASE_URL}{href}')
    soup = BeautifulSoup(r.text, 'html.parser')
    # course code lives in a span like <span class="text detail-code ..."><strong>COMP 50.</strong></span>
    code_spans = soup.find_all('span', class_='detail-code')
    codes = [' '.join(span.get_text().strip().rstrip('.').split()) for span in code_spans]
    ret.extend(codes)

ret = sorted(list(set(ret)))

with open(os.path.join(SCRIPT_DIR, 'codes.json'), 'w', encoding='utf-8') as f:
    json.dump(ret, f, indent=4, ensure_ascii=False)
