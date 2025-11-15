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

# https://sis.rutgers.edu/oldsoc/

SEMESTERS = [
    '92025', # fall 2025
    '02026', # winter 2026
    '12026', # spring 2026
]
CAMPUS = 'NB,NK,CCM,B,CC,H,MC,WM,AC,D,J,RV,E,ONLINE_NB,ONLINE_NK,ONLINE_CM' # may need to take out online stuff
LEVEL = 'U,G'

ret = []
for semester in SEMESTERS:
    r = s.get('https://sis.rutgers.edu/oldsoc/subjects.json',
                params = {
                    'semester': semester,
                    'campus': CAMPUS,
                    'level': LEVEL
                }
    )
    subject_codes = r.json()
    for i, subject in enumerate(subject_codes):
        subject_code = subject.get('code')
        r = s.get('https://sis.rutgers.edu/oldsoc/courses.json',
                    params = {
                        'semester': semester,
                        'campus': CAMPUS,
                        'level': LEVEL,
                        'subject': subject_code,
                    }
        )
        print(f'Fetched semester {semester} subject {i+1}/{len(subject_codes)}: {subject.get("code")} - {len(r.json())} courses')
        courses = r.json()
        ret.extend([
            f'{x["offeringUnitCode"]}:{x["subject"]}:{x["courseNumber"]} {x["title"]}' for x in courses
        ])

ret = [re.sub(r'[\-]', ' ', x) for x in ret]
ret = [re.sub(r'["\'().,+/?@]', '', x) for x in ret]
ret = sorted(list(set(ret)))

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(SCRIPT_DIR, 'codes.json'), 'w', encoding='utf-8') as f:
    json.dump(ret, f, indent=4, ensure_ascii=False)

# import code; code.interact(local=locals())

# [
#     {
#         "description": "ACADEMIC AND STUDENT DEVELOPMENT",
#         "code": "907"
#     },
#     {
#         "description": "ACADEMIC FOUNDATIONS",
#         "code": "003"
#     },
#     {
#         "description": "ACCOUNTING",
#         "code": "010"
#     },
#     {
#         "description": "ADMINISTRATIVE STUDIES",
#         "code": "011"
#     },
#     {
#         "description": "AFRICAN STUDIES",
#         "code": "016"
#     },
#     {
#         "description": "AFRICAN, M. EAST. & S. ASIAN LANG & LIT",
#         "code": "013"
#     },
#     {
#         "description": "AFRO-AMERICAN STUDIES",
#         "code": "014"
#     },
#     {
#         "description": "AGRICULTURE AND FOOD SYSTEMS",
#         "code": "020"
#     },
#     {
#         "description": "AGRICULTURE AND NATURAL RESOURCE MGMT",
#         "code": "035"
#     },
#     {
#         "description": "ALCOHOL STUDIES",
#         "code": "047"
#     },
#     {
#         "description": "AMERICAN LANGUAGE STUDIES",
#         "code": "357"
#     },
#     {
#         "description": "AMERICAN STUDIES",
#         "code": "050"
#     },
#     {
#         "description": "ANIMAL SCIENCE",
#         "code": "067"
#     },
#     {
#         "description": "ANTHROPOLOGY",
#         "code": "070"
#     },
#     {
#         "description": "APPLIED MATHEMATICS",
#         "code": "642"
#     },
#     {
#         "description": "APPLIED PHYSICS",
#         "code": "755"
#     },
#     {
#         "description": "ARABIC LANGUAGES",
#         "code": "074"
#     },
#     {
#         "description": "ARMENIAN",
#         "code": "078"
#     },
#     {
#         "description": "ART",
#         "code": "080"
#     },
#     {
#         "description": "ART HISTORY",
#         "code": "082"
#     },
#     {
#         "description": "ARTS AND SCIENCES",
#         "code": "090"
#     },
#     {
#         "description": "ARTS,CULTURE AND MEDIA",
#         "code": "083"
#     },
#     {
#         "description": "ASIAN STUDIES",
#         "code": "098"
#     },
#     {
#         "description": "ATMOSPHERIC SCIENCE",
#         "code": "107"
#     },
#     {
#         "description": "BEHAVIORAL AND NEURAL SCIENCES",
#         "code": "112"
#     },
#     {
#         "description": "BIOCHEMISTRY",
#         "code": "115"
#     },
#     {
#         "description": "BIOENVIRONMENTAL ENGINEERING",
#         "code": "117"
#     },
#     {
#         "description": "BIOLOGICAL SCIENCES",
#         "code": "119"
#     },
#     {
#         "description": "BIOLOGY",
#         "code": "120"
#     },
#     {
#         "description": "BIOMATHEMATICS",
#         "code": "122"
#     },
#     {
#         "description": "BIOMEDICAL ENGINEERING",
#         "code": "125"
#     },
#     {
#         "description": "BIOTECHNOLOGY",
#         "code": "126"
#     },
#     {
#         "description": "BUSINESS ADMINISTRATION",
#         "code": "135"
#     },
#     {
#         "description": "BUSINESS ANALYTICS AND INFORMATION TECH ",
#         "code": "136"
#     },
#     {
#         "description": "BUSINESS AND SCIENCE",
#         "code": "137"
#     },
#     {
#         "description": "BUSINESS LAW",
#         "code": "140"
#     },
#     {
#         "description": "BUSINESS OF FASHION",
#         "code": "134"
#     },
#     {
#         "description": "CELL & DEVELOPMENTAL BIOLOGY",
#         "code": "148"
#     },
#     {
#         "description": "CELL BIO & NEURO SCI",
#         "code": "146"
#     },
#     {
#         "description": "CHEMICAL AND BIOCHEMICAL ENGINEERING",
#         "code": "155"
#     },
#     {
#         "description": "CHEMICAL BIOLOGY",
#         "code": "158"
#     },
#     {
#         "description": "CHEMISTRY",
#         "code": "160"
#     },
#     {
#         "description": "CHINESE",
#         "code": "165"
#     },
#     {
#         "description": "CINEMA STUDIES",
#         "code": "175"
#     },
#     {
#         "description": "CITY AND REGIONAL PLANNING",
#         "code": "170"
#     },
#     {
#         "description": "CIVIL AND ENVIRONMENTAL ENGINEERING",
#         "code": "180"
#     },
#     {
#         "description": "CLASSICS",
#         "code": "190"
#     },
#     {
#         "description": "CLINICAL PSYCHOLOGY",
#         "code": "821"
#     },
#     {
#         "description": "COGNITIVE SCIENCES",
#         "code": "185"
#     },
#     {
#         "description": "COLLEGE AND UNIVERSITY LEADERSHIP",
#         "code": "187"
#     },
#     {
#         "description": "COLLEGE TEACHING",
#         "code": "186"
#     },
#     {
#         "description": "COMMUNICATION",
#         "code": "192"
#     },
#     {
#         "description": "COMMUNICATION AND INFORMATION",
#         "code": "189"
#     },
#     {
#         "description": "COMMUNICATION AND INFORMATION STUDIES",
#         "code": "194"
#     },
#     {
#         "description": "COMMUNITY HEALTH OUTREACH",
#         "code": "193"
#     },
#     {
#         "description": "COMPARATIVE LITERATURE",
#         "code": "195"
#     },
#     {
#         "description": "COMPUTER SCIENCE",
#         "code": "198"
#     },
#     {
#         "description": "CREATIVE ARTS EDUCATION",
#         "code": "259"
#     },
#     {
#         "description": "CREATIVE WRITING",
#         "code": "200"
#     },
#     {
#         "description": "CRIMINAL JUSTICE",
#         "code": "202"
#     },
#     {
#         "description": "DANCE",
#         "code": "203"
#     },
#     {
#         "description": "DANCE - MGSA",
#         "code": "206"
#     },
#     {
#         "description": "DANCE EDUCATION",
#         "code": "207"
#     },
#     {
#         "description": "DATA SCIENCE",
#         "code": "219"
#     },
#     {
#         "description": "DESIGN",
#         "code": "208"
#     },
#     {
#         "description": "EARTH SYSTEM SCIENCE",
#         "code": "218"
#     },
#     {
#         "description": "EAST ASIAN LANGUAGE AND CULTURES",
#         "code": "217"
#     },
#     {
#         "description": "ECOLOGY",
#         "code": "215"
#     },
#     {
#         "description": "ECOLOGY, EVOLUTION AND NATURAL RESOURCES",
#         "code": "216"
#     },
#     {
#         "description": "ECONOMICS",
#         "code": "220"
#     },
#     {
#         "description": "ECONOMICS, APPLIED",
#         "code": "223"
#     },
#     {
#         "description": "EDUCATION",
#         "code": "300"
#     },
#     {
#         "description": "EDUCATION-ADULT AND CONTINUING EDUCATION",
#         "code": "233"
#     },
#     {
#         "description": "EDUCATION-COLLEGE STUDENT AFFAIRS",
#         "code": "245"
#     },
#     {
#         "description": "EDUCATION-COUNSELING PSYCHOLOGY",
#         "code": "297"
#     },
#     {
#         "description": "EDUCATION-DESIGN OF LEARNING ENVIRON",
#         "code": "262"
#     },
#     {
#         "description": "EDUCATION-EARLY CHILD/ELEMENTARY EDUC",
#         "code": "251"
#     },
#     {
#         "description": "EDUCATION-EDUC STATS & MEASUREMENT",
#         "code": "291"
#     },
#     {
#         "description": "EDUCATION-EDUCATION ELECTIVES",
#         "code": "255"
#     },
#     {
#         "description": "EDUCATION-EDUCATION, GENERAL ELECTIVE",
#         "code": "250"
#     },
#     {
#         "description": "EDUCATION-EDUCATIONAL ADMIN AND SUPERV",
#         "code": "230"
#     },
#     {
#         "description": "EDUCATION-EDUCATIONAL PSYCHOLOGY",
#         "code": "290"
#     },
#     {
#         "description": "EDUCATION-ENGLISH/LANG ARTS EDUCATION",
#         "code": "252"
#     },
#     {
#         "description": "EDUCATION-GIFTED EDUCATION",
#         "code": "294"
#     },
#     {
#         "description": "EDUCATION-HIGHER EDUCATION",
#         "code": "507"
#     },
#     {
#         "description": "EDUCATION-LANGUAGE EDUCATION",
#         "code": "253"
#     },
#     {
#         "description": "EDUCATION-LEARNING COGNITION & DEV",
#         "code": "295"
#     },
#     {
#         "description": "EDUCATION-MATHEMATICS EDUCATION",
#         "code": "254"
#     },
#     {
#         "description": "EDUCATION-READING",
#         "code": "299"
#     },
#     {
#         "description": "EDUCATION-SCIENCE EDUCATION",
#         "code": "256"
#     },
#     {
#         "description": "EDUCATION-SOCIAL & PHILOS FOUND OF ED",
#         "code": "310"
#     },
#     {
#         "description": "EDUCATION-SOCIAL EDUCATION",
#         "code": "257"
#     },
#     {
#         "description": "EDUCATION-SPECIAL EDUCATION",
#         "code": "293"
#     },
#     {
#         "description": "EDUCATION-TEACHER LEADERSHIP",
#         "code": "267"
#     },
#     {
#         "description": "EDUCATIONAL OPPORTUNITY FUND",
#         "code": "364"
#     },
#     {
#         "description": "ELECTRICAL AND COMPU.",
#         "code": "332"
#     },
#     {
#         "description": "ENDOCRINOLOGY AND ANIMAL BIOSCIENCES",
#         "code": "340"
#     },
#     {
#         "description": "ENGLISH",
#         "code": "350"
#     },
#     {
#         "description": "ENGLISH - AMERICAN LITERATURE",
#         "code": "352"
#     },
#     {
#         "description": "ENGLISH - FILM STUDIES",
#         "code": "354"
#     },
#     {
#         "description": "ENGLISH AS A SECOND LANGUAGE",
#         "code": "356"
#     },
#     {
#         "description": "ENGLISH: COMP & WRITING",
#         "code": "355"
#     },
#     {
#         "description": "ENGLISH: CREATIVE WRITING",
#         "code": "351"
#     },
#     {
#         "description": "ENGLISH: LITERARY THEORY",
#         "code": "353"
#     },
#     {
#         "description": "ENGLISH: LITERATURE",
#         "code": "358"
#     },
#     {
#         "description": "ENGLISH: THEORIES AND METHODS",
#         "code": "359"
#     },
#     {
#         "description": "ENTOMOLOGY",
#         "code": "370"
#     },
#     {
#         "description": "ENTREPRENEURSHIP",
#         "code": "382"
#     },
#     {
#         "description": "ENVIRON. POLICY, INSTITUTIONS & BEHAVIOR",
#         "code": "374"
#     },
#     {
#         "description": "ENVIRONMENTAL AND BIOLOGICAL SCIENCES",
#         "code": "015"
#     },
#     {
#         "description": "ENVIRONMENTAL AND BUSINESS ECONOMICS",
#         "code": "373"
#     },
#     {
#         "description": "ENVIRONMENTAL CHANGE, HUMAN DIMENSION",
#         "code": "378"
#     },
#     {
#         "description": "ENVIRONMENTAL ENGINEERING",
#         "code": "366"
#     },
#     {
#         "description": "ENVIRONMENTAL GEOLOGY",
#         "code": "380"
#     },
#     {
#         "description": "ENVIRONMENTAL PLANNING AND DESIGN",
#         "code": "573"
#     },
#     {
#         "description": "ENVIRONMENTAL SCIENCES",
#         "code": "375"
#     },
#     {
#         "description": "ENVIRONMENTAL STUDIES",
#         "code": "381"
#     },
#     {
#         "description": "EUROPEAN STUDIES",
#         "code": "360"
#     },
#     {
#         "description": "EXCHANGE",
#         "code": "001"
#     },
#     {
#         "description": "EXCHANGE REGISTRATION",
#         "code": "376"
#     },
#     {
#         "description": "EXECUTIVE MBA",
#         "code": "385"
#     },
#     {
#         "description": "EXERCISE SCIENCE",
#         "code": "377"
#     },
#     {
#         "description": "FILM STUDIES",
#         "code": "387"
#     },
#     {
#         "description": "FILMMAKING",
#         "code": "211"
#     },
#     {
#         "description": "FINANCE",
#         "code": "390"
#     },
#     {
#         "description": "FINANCIAL ANALYSIS",
#         "code": "430"
#     },
#     {
#         "description": "FOOD AND BUSINESS ECONOMICS",
#         "code": "395"
#     },
#     {
#         "description": "FOOD SCIENCE",
#         "code": "400"
#     },
#     {
#         "description": "FRENCH",
#         "code": "420"
#     },
#     {
#         "description": "GENDER STUDIES",
#         "code": "443"
#     },
#     {
#         "description": "GENERAL ENGINEERING",
#         "code": "440"
#     },
#     {
#         "description": "GENETICS",
#         "code": "447"
#     },
#     {
#         "description": "GEOGRAPHY",
#         "code": "450"
#     },
#     {
#         "description": "GEOLOGICAL SCIENCES",
#         "code": "460"
#     },
#     {
#         "description": "GERMAN",
#         "code": "470"
#     },
#     {
#         "description": "GLOBAL AFFAIRS",
#         "code": "478"
#     },
#     {
#         "description": "GLOBAL SPORT BUSINESS",
#         "code": "475"
#     },
#     {
#         "description": "GRADUATE - NEWARK",
#         "code": "485"
#     },
#     {
#         "description": "GRAPHIC DESIGN",
#         "code": "085"
#     },
#     {
#         "description": "GREEK",
#         "code": "490"
#     },
#     {
#         "description": "GREEK, MODERN",
#         "code": "489"
#     },
#     {
#         "description": "HEALTH ADMINISTRATION",
#         "code": "501"
#     },
#     {
#         "description": "HEALTH COMMUNICATION AND INFORMATION",
#         "code": "503"
#     },
#     {
#         "description": "HINDI",
#         "code": "505"
#     },
#     {
#         "description": "HISTORY GENERAL/COMPARATIVE",
#         "code": "506"
#     },
#     {
#         "description": "HISTORY, AFR ASIA LATIN AM",
#         "code": "508"
#     },
#     {
#         "description": "HISTORY, AMERICAN",
#         "code": "512"
#     },
#     {
#         "description": "HISTORY, GENERAL",
#         "code": "510"
#     },
#     {
#         "description": "HONORS LIVING-LEARNING COMMUNITY",
#         "code": "526"
#     },
#     {
#         "description": "HONORS PROGRAM",
#         "code": "525"
#     },
#     {
#         "description": "HUMAN RESOURCE MANAGEMENT",
#         "code": "533"
#     },
#     {
#         "description": "HUNGARIAN",
#         "code": "535"
#     },
#     {
#         "description": "INDIVIDUALIZED MAJOR",
#         "code": "555"
#     },
#     {
#         "description": "INDUSTRIAL AND SYSTEMS ENGINEERING",
#         "code": "540"
#     },
#     {
#         "description": "INDUSTRIAL RELATIONS AND HUMAN RESOURCES",
#         "code": "545"
#     },
#     {
#         "description": "INFORMATION TECHNOLOGY",
#         "code": "544"
#     },
#     {
#         "description": "INFORMATION TECHNOLOGY AND INFORMATICS",
#         "code": "547"
#     },
#     {
#         "description": "INSTRUCTION AND RESEARCH DEVELOPMENT",
#         "code": "908"
#     },
#     {
#         "description": "INTERDISCIPLINARY - MASON GROSS",
#         "code": "557"
#     },
#     {
#         "description": "INTERDISCIPLINARY - SEBS",
#         "code": "554"
#     },
#     {
#         "description": "INTERDISCIPLINARY STUDIES - ARTS & SCI",
#         "code": "556"
#     },
#     {
#         "description": "INTERFUNCTIONAL",
#         "code": "621"
#     },
#     {
#         "description": "INTERNATIONAL BUSINESS AND BUSINESS",
#         "code": "522"
#     },
#     {
#         "description": "INTERNATIONAL BUSINESS AND BUSINESS",
#         "code": "553"
#     },
#     {
#         "description": "INTERNATIONAL STUDIES",
#         "code": "558"
#     },
#     {
#         "description": "ITALIAN",
#         "code": "560"
#     },
#     {
#         "description": "JAPANESE",
#         "code": "565"
#     },
#     {
#         "description": "JEWISH STUDIES",
#         "code": "563"
#     },
#     {
#         "description": "JOURNALISM",
#         "code": "086"
#     },
#     {
#         "description": "JOURNALISM AND MEDIA STUDIES",
#         "code": "567"
#     },
#     {
#         "description": "JUSTICE STUDIES",
#         "code": "204"
#     },
#     {
#         "description": "KINESIOLOGY AND APPLIED PHYSIOLOGY",
#         "code": "572"
#     },
#     {
#         "description": "KOREAN",
#         "code": "574"
#     },
#     {
#         "description": "LABOR STUDIES",
#         "code": "575"
#     },
#     {
#         "description": "LABOR STUDIES AND EMPLOYMENT RELATIONS",
#         "code": "578"
#     },
#     {
#         "description": "LANDSCAPE ARCHITECTURE",
#         "code": "550"
#     },
#     {
#         "description": "LANGUAGES AND CULTURES",
#         "code": "617"
#     },
#     {
#         "description": "LATIN",
#         "code": "580"
#     },
#     {
#         "description": "LATIN AMERICAN STUDIES",
#         "code": "590"
#     },
#     {
#         "description": "LATINO AND HISPANIC CARIBBEAN STUDIES",
#         "code": "595"
#     },
#     {
#         "description": "LAW - NEWARK",
#         "code": "600"
#     },
#     {
#         "description": "LAW PROFESSIONAL SKILLS",
#         "code": "602"
#     },
#     {
#         "description": "LEADERSHIP SKILLS",
#         "code": "607"
#     },
#     {
#         "description": "LIBERAL STUDIES",
#         "code": "606"
#     },
#     {
#         "description": "LIBRARY AND INFORMATION SCIENCE         ",
#         "code": "610"
#     },
#     {
#         "description": "LINGUISTICS",
#         "code": "615"
#     },
#     {
#         "description": "MANAGEMENT",
#         "code": "620"
#     },
#     {
#         "description": "MANAGEMENT AND WORK",
#         "code": "624"
#     },
#     {
#         "description": "MANAGEMENT SCIENCE AND INFO SYSTEMS",
#         "code": "623"
#     },
#     {
#         "description": "MARINE AND COASTAL SCIENCES",
#         "code": "628"
#     },
#     {
#         "description": "MARKETING",
#         "code": "630"
#     },
#     {
#         "description": "MASON GROSS DIGITAL FILMMAKING",
#         "code": "632"
#     },
#     {
#         "description": "MATERIALS SCIENCE AND ENGINEERING",
#         "code": "635"
#     },
#     {
#         "description": "MATHEMATICAL SCIENCE",
#         "code": "645"
#     },
#     {
#         "description": "MATHEMATICS",
#         "code": "640"
#     },
#     {
#         "description": "MATHEMATICS",
#         "code": "643"
#     },
#     {
#         "description": "MECHANICAL AND AEROSPACE ENGINEERING",
#         "code": "650"
#     },
#     {
#         "description": "MEDICAL ETHICS AND POLICY",
#         "code": "652"
#     },
#     {
#         "description": "MEDICAL TECHNOLOGY",
#         "code": "660"
#     },
#     {
#         "description": "MEDICINAL CHEMISTRY",
#         "code": "663"
#     },
#     {
#         "description": "MEDIEVAL STUDIES",
#         "code": "667"
#     },
#     {
#         "description": "METEOROLOGY",
#         "code": "670"
#     },
#     {
#         "description": "MICROBIAL BIOLOGY",
#         "code": "682"
#     },
#     {
#         "description": "MICROBIOLOGY",
#         "code": "680"
#     },
#     {
#         "description": "MICROMOLECULAR GENETICS",
#         "code": "681"
#     },
#     {
#         "description": "MIDDLE EASTERN STUDIES",
#         "code": "685"
#     },
#     {
#         "description": "MILITARY EDUCATION, AIR FORCE",
#         "code": "690"
#     },
#     {
#         "description": "MILITARY EDUCATION, ARMY",
#         "code": "691"
#     },
#     {
#         "description": "MILITARY EDUCATION, NAVY",
#         "code": "692"
#     },
#     {
#         "description": "MOL BIO & BIOCHEM",
#         "code": "694"
#     },
#     {
#         "description": "MOLECULAR BIOSCIENCES",
#         "code": "695"
#     },
#     {
#         "description": "MUSIC",
#         "code": "087"
#     },
#     {
#         "description": "MUSIC",
#         "code": "700"
#     },
#     {
#         "description": "MUSIC - MGSA",
#         "code": "702"
#     },
#     {
#         "description": "MUSIC, APPLIED (UNITS 07 AND 08)",
#         "code": "701"
#     },
#     {
#         "description": "MUSIC, APPLIED (UNITS 07 AND 08)",
#         "code": "703"
#     },
#     {
#         "description": "NEUROSCIENCE",
#         "code": "710"
#     },
#     {
#         "description": "NURSING",
#         "code": "705"
#     },
#     {
#         "description": "NUTRITIONAL SCIENCES",
#         "code": "709"
#     },
#     {
#         "description": "OCEANOGRAPHY",
#         "code": "712"
#     },
#     {
#         "description": "OPERATIONS RESEARCH",
#         "code": "711"
#     },
#     {
#         "description": "ORGANIZATIONAL BEHAVIOR",
#         "code": "829"
#     },
#     {
#         "description": "ORGANIZATIONAL LEADERSHIP",
#         "code": "713"
#     },
#     {
#         "description": "PACKAGING ENGINEERING",
#         "code": "731"
#     },
#     {
#         "description": "PEACE AND CONFLICT STUDIES",
#         "code": "735"
#     },
#     {
#         "description": "PERSIAN",
#         "code": "723"
#     },
#     {
#         "description": "PHARMACEUTICAL CHEMISTRY",
#         "code": "715"
#     },
#     {
#         "description": "PHARMACEUTICS",
#         "code": "721"
#     },
#     {
#         "description": "PHARMACOLOGY AND TOXICOLOGY",
#         "code": "718"
#     },
#     {
#         "description": "PHARMACY",
#         "code": "720"
#     },
#     {
#         "description": "PHARMACY PRACTICE AND ADMINISTRATION",
#         "code": "725"
#     },
#     {
#         "description": "PHILOSOPHY",
#         "code": "730"
#     },
#     {
#         "description": "PHYSICIAN ASSISTANT",
#         "code": "745"
#     },
#     {
#         "description": "PHYSICS",
#         "code": "750"
#     },
#     {
#         "description": "PHYSIOLOGY AND INTEGRATIVE BIOLOGY",
#         "code": "761"
#     },
#     {
#         "description": "PLANNING AND PUBLIC POLICY",
#         "code": "762"
#     },
#     {
#         "description": "PLANT BIOLOGY",
#         "code": "765"
#     },
#     {
#         "description": "PLANT SCIENCE",
#         "code": "776"
#     },
#     {
#         "description": "POLICY, HEALTH, AND ADMINISTRATION",
#         "code": "775"
#     },
#     {
#         "description": "POLISH",
#         "code": "787"
#     },
#     {
#         "description": "POLITICAL SCIENCE",
#         "code": "790"
#     },
#     {
#         "description": "PORTUGUESE",
#         "code": "810"
#     },
#     {
#         "description": "PORTUGUESE AND LUSOPHONE WORLD STUDIES",
#         "code": "812"
#     },
#     {
#         "description": "PROFESSIONAL PSYCHOLOGY",
#         "code": "820"
#     },
#     {
#         "description": "PSYCHOLOGY",
#         "code": "830"
#     },
#     {
#         "description": "PSYCHOLOGY, APPLIED",
#         "code": "844"
#     },
#     {
#         "description": "PUBLIC ACCOUNTING",
#         "code": "835"
#     },
#     {
#         "description": "PUBLIC ADMIN AND MGMT",
#         "code": "843"
#     },
#     {
#         "description": "PUBLIC ADMINISTRATION",
#         "code": "834"
#     },
#     {
#         "description": "PUBLIC ADMINISTRATION ,EXECUTIVE",
#         "code": "831"
#     },
#     {
#         "description": "PUBLIC HEALTH",
#         "code": "832"
#     },
#     {
#         "description": "PUBLIC INFORMATICS",
#         "code": "816"
#     },
#     {
#         "description": "PUBLIC POLICY",
#         "code": "833"
#     },
#     {
#         "description": "QUANTITATIVE BIOMEDICINE",
#         "code": "848"
#     },
#     {
#         "description": "QUANTITATIVE FINANCE",
#         "code": "839"
#     },
#     {
#         "description": "REAL ESTATE",
#         "code": "851"
#     },
#     {
#         "description": "RELIGION",
#         "code": "840"
#     },
#     {
#         "description": "RUSSIAN",
#         "code": "860"
#     },
#     {
#         "description": "SCHOOL PSYCHOLOGY",
#         "code": "826"
#     },
#     {
#         "description": "SEBS INTERNSHIP",
#         "code": "902"
#     },
#     {
#         "description": "SEXUALITIES STUDIES",
#         "code": "888"
#     },
#     {
#         "description": "SLAVIC AND EAST EUROPEAN STUDIES",
#         "code": "861"
#     },
#     {
#         "description": "SOCIAL JUSTICE",
#         "code": "904"
#     },
#     {
#         "description": "SOCIAL WORK",
#         "code": "910"
#     },
#     {
#         "description": "SOCIOLOGY",
#         "code": "920"
#     },
#     {
#         "description": "SPANISH",
#         "code": "940"
#     },
#     {
#         "description": "SPORT MANAGEMENT",
#         "code": "955"
#     },
#     {
#         "description": "STATISTICS",
#         "code": "960"
#     },
#     {
#         "description": "STATISTICS, FINANCIAL AND RISK MGMT",
#         "code": "958"
#     },
#     {
#         "description": "STATISTICS-DATA SCIENCE",
#         "code": "954"
#     },
#     {
#         "description": "STUDY ABROAD",
#         "code": "959"
#     },
#     {
#         "description": "SUPPLY CHAIN MANAGEMENT",
#         "code": "799"
#     },
#     {
#         "description": "SWAHILI",
#         "code": "956"
#     },
#     {
#         "description": "THEATER",
#         "code": "965"
#     },
#     {
#         "description": "THEATER ARTS - MGSA",
#         "code": "966"
#     },
#     {
#         "description": "TOXICOLOGY",
#         "code": "963"
#     },
#     {
#         "description": "TURKISH",
#         "code": "973"
#     },
#     {
#         "description": "TWI",
#         "code": "974"
#     },
#     {
#         "description": "UKRANIAN",
#         "code": "967"
#     },
#     {
#         "description": "URBAN PLANNING",
#         "code": "971"
#     },
#     {
#         "description": "URBAN PLANNING AND POLICY DEVELOPMENT",
#         "code": "970"
#     },
#     {
#         "description": "URBAN SYSTEMS",
#         "code": "977"
#     },
#     {
#         "description": "VIDEO PRODUCTION",
#         "code": "089"
#     },
#     {
#         "description": "VISUAL ARTS",
#         "code": "081"
#     },
#     {
#         "description": "WOMEN'S AND GENDER STUDIES",
#         "code": "988"
#     },
#     {
#         "description": "WORLD LANGUAGES",
#         "code": "991"
#     }
# ]