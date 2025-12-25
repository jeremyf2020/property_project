import csv
import os
import re
from django.conf import settings
from api.coordinates.models import Coordinates
from django.core.exceptions import ValidationError

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

def auto_assign_sector(instance):
    """
    Shared logic to link any model (Address, School or more) to a Coordinate Sector.
    """
    # Checks if postcode exists
    if not instance.postcode:
        return

    # Extracts sector (e.g. 'RG1 1AA' -> 'RG1 1')
    sector_name = extract_sector_from_postcode(instance.postcode)
    
    if sector_name:
        # Database Lookup
        sector_obj = Coordinates.objects.filter(name=sector_name).first()
        
        # Sets instance.postcode_sector
        if sector_obj:
            instance.postcode_sector = sector_obj
        else:
            # error handling: Raise error if can't map
            raise ValidationError(f"Sector '{sector_name}' not found. Please import Coordinates first.")
    else:
         raise ValidationError(f"Invalid postcode format: '{instance.postcode}'")