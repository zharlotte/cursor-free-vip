"""
Compares two JSON translation files in /locales (e.g., en.json and ar.json).
Finds keys missing in the target file, translates their values using Google Translate (web scraping),
and inserts the translations. Runs in parallel for speed and creates a backup of the target file.
"""
import json
import requests
import sys
from pathlib import Path
import urllib.parse
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style

init(autoreset=True)

# Recursively get all keys in the JSON as dot-separated paths
def get_keys(d, prefix=''):
    keys = set()
    for k, v in d.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys |= get_keys(v, full_key)
        else:
            keys.add(full_key)
    return keys

# Get value from nested dict by dot-separated path
def get_by_path(d, path):
    for p in path.split('.'):
        d = d[p]
    return d

# Set value in nested dict by dot-separated path
def set_by_path(d, path, value):
    parts = path.split('.')
    for p in parts[:-1]:
        if p not in d:
            d[p] = {}
        d = d[p]
    d[parts[-1]] = value

# Translate text using Google Translate web scraping (mobile version)
def translate(text, source, target):
    url = f"https://translate.google.com/m?sl={source}&tl={target}&q={requests.utils.quote(text)}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        m = re.search(r'class=\"result-container\">(.*?)<', response.text)
        if m:
            return m.group(1)
        else:
            print(Fore.RED + f"Translation not found for: {text}")
            return text
    else:
        print(Fore.RED + f"Request failed for: {text}")
        return text

# Main logic: compare keys, translate missing, and update file
def main(en_filename, other_filename):
    # Always use the /locales directory
    en_path = Path("locales") / en_filename
    other_path = Path("locales") / other_filename
    # Infer language code from filename (before .json)
    en_lang = Path(en_filename).stem
    other_lang = Path(other_filename).stem

    with open(en_path, encoding='utf-8') as f:
        en = json.load(f)
    with open(other_path, encoding='utf-8') as f:
        other = json.load(f)

    en_keys = get_keys(en)
    other_keys = get_keys(other)

    missing = en_keys - other_keys
    print(Fore.YELLOW + f"Missing keys: {len(missing)}")

    # Parallel translation using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_key = {
            executor.submit(translate, get_by_path(en, key), en_lang, other_lang): key
            for key in missing
        }
        for future in as_completed(future_to_key):
            key = future_to_key[future]
            value = get_by_path(en, key)
            try:
                translated = future.result()
                print(Fore.CYAN + f"Translated [{key}]: '{value}' -> " + Fore.MAGENTA + f"'{translated}'")
            except Exception as exc:
                print(Fore.RED + f"Error translating {key}: {exc}")
                translated = value
            set_by_path(other, key, translated)

    # Save the updated file and create a backup
    backup_path = other_path.with_suffix('.bak.json')
    other_path.rename(backup_path)
    with open(other_path, 'w', encoding='utf-8') as f:
        json.dump(other, f, ensure_ascii=False, indent=4)
    print(Fore.GREEN + f"File updated. Backup saved to {backup_path}")

if __name__ == "__main__":
    # Example: python3 fill_missing_translations.py en.json ar.json
    if len(sys.argv) != 3:
        print("Usage: python3 fill_missing_translations.py en.json ar.json")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])