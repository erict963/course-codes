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

# https://adminapps.mercer.edu/classroomsched/default.aspx?C=M

def parse_codes(soup):
    if soup is None:
        return []
    trs = soup.find_all('tr')
    tds = [tr.find_all('td', align='left', style='white-space:nowrap;') for tr in trs]
    tds = [td for sublist in tds for td in sublist]
    return [td.text for td in tds]

TERMS = ['2026-SP', '2026-SU', '2026-FA']
LEVELS = ['U', 'G']
CAMPUS = ['Atlanta Campus', 'Law School', 'Macon Campus', 'Medicine', 'Nursing', 'Pharmacy and Health Sciences', 'Regional Academic Centers', 'Theology']

def get_next_page(s: requests.Session, 
                  viewstate: str, 
                  viewstategenerator: str,
                  page: int = 1,
                  campus: str = 'Macon Campus',
                  rad_term: str = '2026-SP',
                  rad_level: str = 'U') -> Tuple[str, str, list]:
    if page == 1:
        r = s.get('https://adminapps.mercer.edu/classroomsched/default.aspx?C=M')
        soup = BeautifulSoup(r.text, 'html.parser')
        codes = parse_codes(soup)
        viewstate = soup.find('input', {'id': '__VIEWSTATE'}).get('value', '')
        viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'}).get('value', '')
        return viewstate, viewstategenerator, codes
    
    r = s.post('https://adminapps.mercer.edu/classroomsched/default.aspx?C=M', data={
        '__EVENTTARGET': 'dgCounts',
        '__EVENTARGUMENT': f'Page${page}',
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstategenerator,
        'campusList': campus,
        'radTerm': rad_term,
        'radLevel': rad_level,
        'searchCourse': '',
        'searchCourseCode': '',
        'searchCourseSection': '',
        'instructorList': '',
        'deliveryMethod': '',
        'meetingDaysList': '',
        'pickStartTime': '0:00',
        'pickEndTime': '23:59'
    })
    soup = BeautifulSoup(r.text, 'html.parser')
    codes = parse_codes(soup)
    new_viewstate = soup.find('input', {'id': '__VIEWSTATE'})
    if new_viewstate is not None:
        new_viewstate = new_viewstate.get('value', '')
        viewstate = new_viewstate
    new_viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})
    if new_viewstategenerator is not None:
        new_viewstategenerator = new_viewstategenerator.get('value', '')
        viewstategenerator = new_viewstategenerator
        
    return viewstate, viewstategenerator, codes

from itertools import product
from collections import deque


START = 2
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ret = set()
last_codes = deque(maxlen=10) # 
with open(os.path.join(SCRIPT_DIR, 'codes.json'), 'r', encoding='utf-8') as f:
    ret = set(json.load(f))
viewstate, viewstategenerator, page_codes = get_next_page(s, '', '', page=1)

for term, level, campus in product(TERMS, LEVELS, CAMPUS):
    print(f'***** term={term}, level={level}, campus={campus} *****')
    viewstate, viewstategenerator, page_codes = get_next_page(
        s, '', '', page=1, campus=campus, rad_term=term, rad_level=level
    )

    for page in range(START, 1200):
        viewstate, viewstategenerator, page_codes = get_next_page(
            s, viewstate, viewstategenerator, page=page, campus=campus, rad_term=term, rad_level=level
        )
        if not page_codes:
            print(f'No more codes found on page {page}. Stopping.')
            break

        print(f'Fetching page {page} - total codes found so far: {len(ret)}')
        ret.update(page_codes)
    
        last_codes.append(set(page_codes))
        if len(last_codes) == 10 and all(c == last_codes[0] for c in last_codes):
            print(f'Codes have been the same for the last 10 pages at page {page}. Stopping.')
            break

        if page % 10 == 0:
            with open(os.path.join(SCRIPT_DIR, 'codes.json'), 'w', encoding='utf-8') as f:
                json.dump(list(ret), f, indent=4, ensure_ascii=False)

ret = list(ret)
ret = [re.sub(r'[\.]', ' ', x) for x in ret]
ret = sorted(list(set(ret)))

with open(os.path.join(SCRIPT_DIR, 'codes.json'), 'w', encoding='utf-8') as f:
    json.dump(ret, f, indent=4, ensure_ascii=False)



# r = s.get('https://adminapps.mercer.edu/classroomsched/default.aspx?C=M')
# soup = BeautifulSoup(r.text, 'html.parser')
# codes = parse_codes(soup)
# for code in codes:
#     print(code)


# # <input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="AE11B107"/>
# # <input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="X3
# viewstate = soup.find('input', {'id': '__VIEWSTATE'}).get('value', '')
# viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'}).get('value', '')

# r = s.post('https://adminapps.mercer.edu/classroomsched/default.aspx?C=M', data={
#     '__EVENTTARGET': 'dgCounts',
#     '__EVENTARGUMENT': 'Page$2',
#     '__VIEWSTATE': viewstate,
#     '__VIEWSTATEGENERATOR': viewstategenerator,
#     'campusList': 'Macon Campus',
#     'radTerm': '2026-SP',
#     'radLevel': 'U',
#     'searchCourse': '',
#     'searchCourseCode': '',
#     'searchCourseSection': '',
#     'instructorList': '',
#     'deliveryMethod': '',
#     'meetingDaysList': '',
#     'pickStartTime': '0:00',
#     'pickEndTime': '23:59'
# })

# print('next page')
# soup = BeautifulSoup(r.text, 'html.parser')
# codes = parse_codes(soup)
# for code in codes:
#     print(code)


import code; code.interact(local=locals())