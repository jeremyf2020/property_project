# import csv
# import logging
# from api.schools.models import School, KS2Performance, KS4Performance, KS5Performance
# from api.utils import clean_decimal 

# logger = logging.getLogger(__name__)

# # --- Helper for Grades (Strings) ---
# def clean_grade_string(value):
#     """
#     Specific cleaner for A-Level Grades (e.g., 'B-', 'C+').
#     Retains the string but removes 'SUPP', 'NE', etc.
#     """
#     if not value:
#         return None
#     val_str = str(value).strip().upper()
#     if val_str in ['SUPP', 'NE', 'NP', 'LOWCOV', 'SP', 'NA', '', '-', 'DNS']:
#         return None
#     # Return original case (e.g. "B-") but stripped of whitespace
#     return str(value).strip()


# # --- 1. Key Stage 2 (Primary) ---
# def process_ks2_row(row, year=2023):
#     """
#     Source: key_stage2.csv
#     Mappings:
#     - PTRWM_EXP -> % Meeting Expected Standard (Reading, Writing, Maths)
#     - READ_AVERAGE -> Reading Scaled Score
#     - MAT_AVERAGE -> Maths Scaled Score
#     """
#     urn = row.get('URN')
#     try:
#         school = School.objects.get(urn=urn)
#     except School.DoesNotExist:
#         return # Skip if we don't have the basic school record

#     KS2Performance.objects.update_or_create(
#         school=school,
#         academic_year=year,
#         defaults={
#             'pct_meeting_expected': clean_decimal(row.get('PTRWM_EXP')),
#             'reading_score': clean_decimal(row.get('READ_AVERAGE')),
#             'maths_score': clean_decimal(row.get('MAT_AVERAGE')),
#         }
#     )

# # --- 2. Key Stage 4 (Secondary / GCSE) ---
# def process_ks4_row(row, year=2023):
#     """
#     Source: key_stage4.csv
#     Mappings:
#     - P8MEA -> Progress 8 Score
#     - ATT8SCR -> Attainment 8 Score
#     """
#     urn = row.get('URN')
#     try:
#         school = School.objects.get(urn=urn)
#     except School.DoesNotExist:
#         return

#     KS4Performance.objects.update_or_create(
#         school=school,
#         academic_year=year,
#         defaults={
#             'progress_8': clean_decimal(row.get('P8MEA')),
#             'attainment_8': clean_decimal(row.get('ATT8SCR')),
#         }
#     )

# # --- 3. Key Stage 5 (College / A-Level) ---
# def process_ks5_row(row, year=2023):
#     """
#     Source: key_stage5.csv
#     Mappings:
#     - TALLPPE_ALEV_1618 -> A-Level Points (Decimal)
#     - TALLPPEGRD_ALEV_1618 -> A-Level Grade (String)
#     - TALLPPE_ACAD_1618 -> Academic Points
#     - TALLPPEGRD_ACAD_1618 -> Academic Grade
#     """
#     urn = row.get('URN')
#     try:
#         school = School.objects.get(urn=urn)
#     except School.DoesNotExist:
#         return

#     KS5Performance.objects.update_or_create(
#         school=school,
#         academic_year=year,
#         defaults={
#             # Points (Use standard cleaner)
#             'a_level_points': clean_decimal(row.get('TALLPPE_ALEV_1618')),
#             'academic_points': clean_decimal(row.get('TALLPPE_ACAD_1618')),
            
#             # Grades (Use string cleaner)
#             'a_level_grade': clean_grade_string(row.get('TALLPPEGRD_ALEV_1618')),
#             'academic_grade': clean_grade_string(row.get('TALLPPEGRD_ACAD_1618')),
#         }
#     )

# # --- Main Runner ---
# def run_performance_import(ks2_path=None, ks4_path=None, ks5_path=None, year=2023):
#     """
#     Orchestrator to run any or all imports.
#     """
#     print(f"--- Starting Performance Data Import (Year: {year}) ---")

#     if ks2_path:
#         print(f"Importing KS2 from {ks2_path}...")
#         with open(ks2_path, 'r', encoding='utf-8-sig') as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 process_ks2_row(row, year)
    
#     if ks4_path:
#         print(f"Importing KS4 from {ks4_path}...")
#         with open(ks4_path, 'r', encoding='utf-8-sig') as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 process_ks4_row(row, year)

#     if ks5_path:
#         print(f"Importing KS5 from {ks5_path}...")
#         with open(ks5_path, 'r', encoding='utf-8-sig') as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 process_ks5_row(row, year)

#     print("--- Import Complete ---")