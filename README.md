## Setup

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

## Development

Steps to add a new school:

0. Create a new folder with the exact name of the school (e.g., `New School Name`).

   ```
   python3 main.py create-school "New School Name"
   ```

1. Implement the `get_codes.py` script inside the new folder to scrape and save course codes into a `codes.json` file.

   ```
   python3 main.py get-codes "New School Name"
   ```

2. Run the `create_trie` function to generate the trie-structured JSON files.

   ```
   python3 main.py create-trie "New School Name"
   ```

## Helpers

### List Schools

```
python3 main.py list-schools
```

### Cleanup **pycache** Directories

```
python3 main.py cleanup
```
