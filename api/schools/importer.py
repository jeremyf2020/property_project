import logging
from api.schools.models import School, KS2Performance, KS4Performance, KS5Performance
from api.utils import read_csv_generator, clean_int, check_csv_match, clean_decimal

logger = logging.getLogger(__name__)

def process_school_row(row, **kwargs):
    """
    Import basic School data using strict column mapping.
    """
    urn = row.get('URN')
    if not urn:
        return

    School.objects.update_or_create(
        urn=urn,
        defaults={
            'name': row.get('SCHNAME'),
            
            # Location
            'street': row.get('STREET'),
            'locality': row.get('LOCALITY'),
            'address3': row.get('ADDRESS3'),
            'postcode': row.get('POSTCODE'),
            
            # Details
            'school_type': row.get('SCHOOLTYPE'),
            'gender': row.get('GENDER'),
            
            # Status: Check for "Closed"
            'is_closed': check_csv_match(row.get('SCHSTATUS'), 'Closed'),
            
            # Phase Flags: Check for "1"
            'is_primary': check_csv_match(row.get('ISPRIMARY'), '1'),
            'is_secondary': check_csv_match(row.get('ISSECONDARY'), '1'),
            'is_post16': check_csv_match(row.get('ISPOST16'), '1'),

            # Age Range
            'minimum_age': clean_int(row.get('AGELOW')),
            'maximum_age': clean_int(row.get('AGEHIGH')),
        }
    )

def process_ks2_row(row, year=2024):
    """
    Import Key Stage 2 Results (Reading, Writing, Maths).
    Expects columns: URN, PTRWM_EXP, READ_AVERAGE, MAT_AVERAGE
    """
    urn = row.get('URN')
    
    # Safety Check
    try:
        school = School.objects.get(urn=urn)
    except School.DoesNotExist:
        return

    # Create or Update
    # Uses clean_decimal to handle 'SUPP'/'NE'/'65.5%' automatically
    KS2Performance.objects.update_or_create(
        school=school,
        academic_year=year,
        defaults={
            'pct_meeting_expected': clean_decimal(row.get('PTRWM_EXP')),
            'reading_score': clean_decimal(row.get('READ_AVERAGE')),
            'maths_score': clean_decimal(row.get('MAT_AVERAGE')),
        }
    )

def process_ks4_row(row, year=2024):
    """
    Import Key Stage 4 (GCSE) Results.
    Expects columns: URN, P8MEA (Progress 8), ATT8SCR (Attainment 8)
    """
    urn = row.get('URN')
    
    try:
        school = School.objects.get(urn=urn)
    except School.DoesNotExist:
        return

    KS4Performance.objects.update_or_create(
        school=school,
        academic_year=year,
        defaults={
            # Progress 8 Score (Can be negative, clean_decimal handles this)
            'progress_8': clean_decimal(row.get('P8MEA')),
            
            # Attainment 8 Score
            'attainment_8': clean_decimal(row.get('ATT8SCR')),
        }
    )


def process_ks5_row(row, year=2024):
    """
    Import Key Stage 5 (A-Level) Results.
    Expects columns: 
    - TALLPPE_ALEV_1618 (Points)
    - TALLPPEGRD_ALEV_1618 (Grade)
    """
    urn = row.get('URN')
    
    try:
        school = School.objects.get(urn=urn)
    except School.DoesNotExist:
        return

    # Helper specific to Grades (Keep text, remove garbage)
    def _clean_grade(val):
        if not val: 
            return None
        # Normalize
        s_val = str(val).strip().upper()
        # Filter out suppression codes
        if s_val in ['SUPP', 'NE', 'NP', 'NA', '', 'DNS']:
            return None
        # Return original casing stripped (e.g. "B-")
        return str(val).strip()

    KS5Performance.objects.update_or_create(
        school=school,
        academic_year=year,
        defaults={
            # Points (Decimals)
            'a_level_points': clean_decimal(row.get('TALLPPE_ALEV_1618')),
            'academic_points': clean_decimal(row.get('TALLPPE_ACAD_1618')),
            
            # Grades (Strings)
            'a_level_grade': _clean_grade(row.get('TALLPPEGRD_ALEV_1618')),
            'academic_grade': _clean_grade(row.get('TALLPPEGRD_ACAD_1618')),
        }
    )

def _run_generic_import(file_path, row_processor_func, **kwargs):
    """
    Generic helper to loop through ANY CSV and apply a specific processor function.
    Kwargs (like 'year') are passed directly to the processor.
    """
    generator = read_csv_generator(file_path, folder="")
    
    count = 0
    for row in generator:
        # **kwargs passes 'year' down to process_ks2_row(row, year=2022)
        row_processor_func(row, **kwargs)
        count += 1
        
    logger.info(f"Processed {count} rows from {file_path}")

def run_school_base_import(file_path, year=2024):
    _run_generic_import(file_path, process_school_row, year=year)

def run_ks2_import_wrapper(file_path, year=2024):
    _run_generic_import(file_path, process_ks2_row, year=year)

def run_ks4_import_wrapper(file_path, year=2024):
    _run_generic_import(file_path, process_ks4_row, year=year)

def run_ks5_import_wrapper(file_path, year=2024):
    _run_generic_import(file_path, process_ks5_row, year=year)