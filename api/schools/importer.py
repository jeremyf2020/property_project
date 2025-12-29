import logging
from api.schools.models import (
    School, 
    KS2Performance, 
    KS4Performance, 
    KS5Performance
)
from api.utils import read_csv_generator, clean_decimal, clean_int

# logger = logging.getLogger(__name__)

# ==========================================
# 1. Row Processors
# ==========================================

def process_school_row(row):
    """
    Import basic School data from school_information.csv
    Strict mapping based on provided headers:
    URN, SCHNAME, STREET, LOCALITY, ADDRESS3, TOWN, POSTCODE, 
    SCHSTATUS, SCHOOLTYPE, ISPRIMARY, ISSECONDARY, ISPOST16, 
    AGELOW, AGEHIGH, GENDER
    """
    urn = row.get('URN')
    if not urn:
        return

    # 1. Parse Status (Open vs Closed)
    # Data example: "Open", "Closed"
    status = row.get('SCHSTATUS', '').strip()
    is_closed = (status.lower() != 'open')

    # 2. Parse Phase Flags (1 = True, 0 = False)
    # Data example: "1", "0"
    def parse_bool(key):
        val = row.get(key, '0').strip()
        return val == '1'

    # 3. Create or Update
    School.objects.update_or_create(
        urn=urn,
        defaults={
            'name': row.get('SCHNAME'),
            
            # Location
            'street': row.get('STREET'),
            'locality': row.get('LOCALITY'), # e.g. "Caversham"
            'address3': row.get('ADDRESS3'),
            # Note: Your model doesn't have a 'town' field, so we skip row['TOWN']
            # to strictly follow your schema.
            'postcode': row.get('POSTCODE'),
            
            # Details
            'school_type': row.get('SCHOOLTYPE'),
            'gender': row.get('GENDER'),
            'is_closed': is_closed,
            
            # Age Range
            'minimum_age': clean_int(row.get('AGELOW')),
            'maximum_age': clean_int(row.get('AGEHIGH')),
            
            # Phase Flags
            'is_primary': parse_bool('ISPRIMARY'),
            'is_secondary': parse_bool('ISSECONDARY'),
            'is_post16': parse_bool('ISPOST16'),
        }
    )

# ... (rest of the file: process_ks2_row, wrappers, etc. remains the same)