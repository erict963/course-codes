import argparse
import gzip
import json
import os
import importlib.util
import shutil

COURSE_CODES_SCRIPT_NAME = 'get_codes.py' # First, implement get_codes.py for a school
COURSE_CODES_SCRIPT_OUTPUT_NAME = 'codes.json' # Next, run get_codes.py to produce this
COURSE_CODES_TRIE_OUTPUT_NAME = 'codes_trie.json' # Finally, run create_trie to produce this

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    END_MARKER = '$'
    
    def __init__(self):
        self.root = TrieNode()

    def insert(self, code):
        node = self.root
        for char in code:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True

    def build(self, codes):
        for code in codes:
            self.insert(code)

    def to_dict(self, node=None):
        if node is None:
            node = self.root
        result = {}
        if node.is_end:
            result[self.END_MARKER] = True
        for char, child in node.children.items():
            result[char] = self.to_dict(child)
        return result

    @staticmethod
    def from_dict(d):
        trie = Trie()
        trie.root = Trie._dict_to_trie(d)
        return trie

    @staticmethod
    def _dict_to_trie(d):
        node = TrieNode()
        if Trie.END_MARKER in d:
            node.is_end = True
        for char, child_dict in d.items():
            if char != Trie.END_MARKER:
                node.children[char] = Trie._dict_to_trie(child_dict)
        return node

    def search(self, node=None, prefix='', results=None):
        if results is None:
            results = []
        if node is None:
            node = self.root
        if node.is_end:
            results.append(prefix)
        for char, child in node.children.items():
            self.search(child, prefix + char, results)
        return results

def list_schools():
    return [
        x for x in os.listdir('.')
        if os.path.isdir(x) and not x.startswith('.') and x not in ('__pycache__', 'env')
    ]

def cleanup():
    schools = list_schools()
    for school in schools:
        shutil.rmtree(os.path.join(school, '__pycache__'), ignore_errors=True)
    print("Cleaned up __pycache__ directories.")


def create_school(school_name: str):
    os.makedirs(school_name, exist_ok=True)
    with open(os.path.join(school_name, COURSE_CODES_SCRIPT_NAME), 'w') as f:
        f.write(f'# Placeholder for {COURSE_CODES_SCRIPT_NAME}\n')
    print(f"Created directory and placeholder for {school_name}")

def get_codes(school_name: str):
    path = os.path.join(school_name, COURSE_CODES_SCRIPT_NAME)
    if not os.path.exists(path):
        print(f"No {COURSE_CODES_SCRIPT_NAME} found for {school_name}. Please implement it first.")
        return
    
    spec = importlib.util.spec_from_file_location("get_codes_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
def create_trie(school_name: str):
    path = os.path.join(school_name, COURSE_CODES_SCRIPT_OUTPUT_NAME)
    if not os.path.exists(path):
        print(f"No {COURSE_CODES_SCRIPT_OUTPUT_NAME} found for {school_name}. Please run/implement {COURSE_CODES_SCRIPT_NAME} first.")
        return

    with open(path, 'r', encoding='utf-8') as f:
        codes = json.load(f)

    print(f"Original number of codes: {len(codes)}")

    trie = Trie()
    trie.build(codes)

    trie_dict = trie.to_dict()

    # TODO: make regex requirement map

    with open(os.path.join(school_name, COURSE_CODES_TRIE_OUTPUT_NAME), 'w', encoding='utf-8') as f:
        json.dump(trie_dict, f)

    with gzip.open(os.path.join(school_name, COURSE_CODES_TRIE_OUTPUT_NAME + '.gz'), 'wt', encoding='utf-8') as f:
        json.dump(trie_dict, f)

    # Compare file sizes
    original_size = os.path.getsize(os.path.join(school_name, COURSE_CODES_SCRIPT_OUTPUT_NAME))
    trie_size = os.path.getsize(os.path.join(school_name, COURSE_CODES_TRIE_OUTPUT_NAME))
    trie_gz_size = os.path.getsize(os.path.join(school_name, 
                                                COURSE_CODES_TRIE_OUTPUT_NAME + '.gz'))

    print(f"\nFile sizes:")
    print(f"Original JSON: {original_size:,} bytes")
    print(f"Trie JSON: {trie_size:,} bytes")
    print(f"Trie JSON (gzipped): {trie_gz_size:,} bytes")
    print(f"\nSpace savings:")
    print(f"Trie vs Original: {(1 - trie_size/original_size)*100:.1f}%")
    print(f"Trie+gzip vs Original: {(1 - trie_gz_size/original_size)*100:.1f}%")
    assert trie_gz_size < original_size, "Gzipped trie is not smaller than original!"

    # Verify reconstruction works
    reconstructed_trie = Trie.from_dict(trie_dict)
    reconstructed = reconstructed_trie.search()
    print(f"\nVerification: {len(reconstructed)} codes reconstructed")
    assert sorted(reconstructed) == sorted(codes), "Reconstructed codes do not match original!"


# python main.py list-schools 
# python main.py create-school "New School"
# python main.py create-trie "New School"

def main():
    parser = argparse.ArgumentParser(description="Manage course codes.")
    subparsers = parser.add_subparsers(dest='command')

    subparsers.add_parser('list-schools', help='List all schools with course code data.')
    subparsers.add_parser('cleanup', help='Clean up __pycache__ directories.')

    create_school_parser = subparsers.add_parser('create-school', help='Create a new school.')
    create_school_parser.add_argument('school_name', type=str, help='Name of the school to create.')

    get_codes_parser = subparsers.add_parser('get-codes', help='Get codes for a school.')
    get_codes_parser.add_argument('school_name', type=str, help='Name of the school to get codes for.')

    create_trie_parser = subparsers.add_parser('create-trie', help='Create trie for a school.')
    create_trie_parser.add_argument('school_name', type=str, help='Name of the school to create trie for.')

    args = parser.parse_args()
    if args.command == 'create-school':
        create_school(args.school_name)
    elif args.command == 'get-codes':
        get_codes(args.school_name)
    elif args.command == 'create-trie':
        create_trie(args.school_name)
    elif args.command == 'list-schools':
        schools = list_schools()
        print(json.dumps(schools, indent=4))
    elif args.command == 'cleanup':
        cleanup()
    else:
        parser.print_help()
                        
if __name__ == '__main__':
    main()