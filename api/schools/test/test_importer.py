# from django.test import TestCase
# from api.coordinates.models import Coordinates
# from api.schools.models import School, KS2Performance, KS4Performance, KS5Performance
# from api.schools.importer import process_ks2_row, process_ks4_row, process_ks5_row

# class RealDataImportTest(TestCase):
#     def setUp(self):
#         self.sector = Coordinates.objects.create(name="RG1 6")
#         # Create a school that matches the URN in your CSV snippets
#         self.school = School.objects.create(
#             urn="125158",  # Matches the KS2 CSV sample
#             name="St Mary Primary", 
#             postcode="RG1 6DU",
#             postcode_sector=self.sector
#         )
#         # Create secondary for KS4/5 (Using URN from your KS4 sample)
#         self.secondary = School.objects.create(
#             urn="110165", # Matches "The Abbey School Reading"
#             name="The Abbey",
#             postcode="RG1 5DZ",
#             postcode_sector=self.sector
#         )

#     def test_ks2_csv_mapping(self):
#         """ Test mapping of keys from key_stage2.csv snippet """
#         # Data taken directly from your paste
#         row = {
#             'URN': '125158',
#             'PTRWM_EXP': '46%',    # Note the % sign
#             'READ_AVERAGE': '104',
#             'MAT_AVERAGE': '102'
#         }
#         process_ks2_row(row, year=2023)

#         res = KS2Performance.objects.get(school=self.school)
#         self.assertEqual(float(res.pct_meeting_expected), 46.0)
#         self.assertEqual(float(res.reading_score), 104.0)

#     def test_ks4_csv_mapping(self):
#         """ Test mapping of keys from key_stage4.csv snippet """
#         # Data taken from The Abbey School row
#         row = {
#             'URN': '110165',
#             'P8MEA': '1.31',  # Progress 8
#             'ATT8SCR': '83.2' # Attainment 8
#         }
#         process_ks4_row(row, year=2023)

#         res = KS4Performance.objects.get(school=self.secondary)
#         self.assertEqual(float(res.progress_8), 1.31)
#         self.assertEqual(float(res.attainment_8), 83.2)

#     def test_ks5_csv_mapping(self):
#         """ Test mapping of keys from key_stage5.csv snippet """
#         # Data taken from row 2 (URN 870... let's pretend it matches The Abbey)
#         row = {
#             'URN': '110165',
#             'TALLPPE_ALEV_1618': '36.86',
#             'TALLPPEGRD_ALEV_1618': 'B-',
#             'TALLPPE_ACAD_1618': '37.38',
#             'TALLPPEGRD_ACAD_1618': 'B-'
#         }
#         process_ks5_row(row, year=2023)

#         res = KS5Performance.objects.get(school=self.secondary)
#         self.assertEqual(float(res.a_level_points), 36.86)
#         self.assertEqual(res.a_level_grade, "B-")