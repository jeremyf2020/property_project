import csv
import os
import re
from django.conf import settings

def read_csv_generator(filename, folder="data"):
    """
    Generator that yields rows from a CSV file one by one.
    """
    full_path = os.path.join(settings.BASE_DIR, folder, filename)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Could not find file at: {full_path}")

    with open(full_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clean_row = {k.strip(): v.strip() for k, v in row.items() if k}
            yield clean_row

def extract_sector_from_postcode(postcode):
    """
    Extracts the sector (e.g., 'RG1 1') from a full postcode (e.g., 'RG1 1AF').
    Returns None if the format is invalid.
    """
    if not postcode:
        return None
        
    # Standardize input: uppercase and strip whitespace
    clean_postcode = postcode.strip().upper()

    # Regex breakdown:
    # ^              Start
    # [A-Z]{1,2}     Area (e.g. RG)
    # [0-9]          District digit (1)
    # [A-Z0-9]?      Optional extra (for London e.g. W1A)
    # \s             Mandatory Space
    # [0-9]          Sector digit (1)
    # ... ignoring the last 2 letters
    
    # only capture the part BEFORE the last two letters (e.g. RG1 1)
    pattern = r"^([A-Z]{1,2}[0-9][A-Z0-9]?\s[0-9])[A-Z]{2}$"
    
    match = re.match(pattern, clean_postcode)
    if match:
        return match.group(1)
    
    return None