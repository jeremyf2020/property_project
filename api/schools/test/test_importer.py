# from django.test import TestCase
# from api.coordinates.models import Coordinates
# from api.schools.models import School, KS2Performance, KS4Performance, KS5Performance
# from api.schools.importer import (
#     process_school_row, 
#     process_ks2_row, 
#     process_ks4_row, 
#     process_ks5_row
# )

# class SchoolImporterTest(TestCase):
#     def setUp(self):
#         # Create a sector for auto-assign
#         self.sector = Coordinates.objects.create(name="RG1 1")
        
#         # Create a base school for performance tests
#         self.school = School.objects.create(
#             urn="123456", 
#             name="Test Academy", 
#             postcode="RG1 1AA", 
#             postcode_sector=self.sector
#         )

#     # --- 1. Base School Logic Tests ---
    
#     def test_school_row_creation(self):
#         """Test creating a school from a raw CSV row"""
#         row = {
#             'URN': '999001',
#             'EstablishmentName': 'New Primary School',
#             'Postcode': 'RG1 1AA',
#             'PhaseOfEducation (name)': 'Primary',
#             'StatutoryLowAge': '4',
#             'StatutoryHighAge': '11',
#             'EstablishmentStatus (name)': 'Open'
#         }
#         process_school_row(row)
        
#         # Verify
#         school = School.objects.get(urn='999001')
#         self.assertEqual(school.name, 'New Primary School')
#         self.assertTrue(school.is_primary)
#         self.assertFalse(school.is_secondary)
#         self.assertEqual(school.minimum_age, 4)

#     def test_school_closed_logic(self):
#         """Test that 'Closed' status is captured"""
#         row = {
#             'URN': '999002',
#             'EstablishmentName': 'Closed School',
#             'Postcode': 'RG1 1AA',
#             'EstablishmentStatus (name)': 'Closed'
#         }
#         process_school_row(row)
#         self.assertTrue(School.objects.get(urn='999002').is_closed)

#     # --- 2. Performance Logic Tests ---

#     def test_ks2_row_import(self):
#         """Test KS2 data mapping and cleaning"""
#         row = {
#             'URN': '123456',
#             'PTRWM_EXP': '65.5%', # Includes dirty %
#             'READ_AVERAGE': '105',
#             'MAT_AVERAGE': '104'
#         }
#         process_ks2_row(row, year=2023)
        
#         res = KS2Performance.objects.get(school=self.school)
#         self.assertEqual(float(res.pct_meeting_expected), 65.5)
#         self.assertEqual(float(res.reading_score), 105.0)

#     def test_ks4_row_import(self):
#         """Test KS4 data mapping"""
#         row = {
#             'URN': '123456',
#             'P8MEA': '-0.25',
#             'ATT8SCR': '45.2'
#         }
#         process_ks4_row(row, year=2023)
        
#         res = KS4Performance.objects.get(school=self.school)
#         self.assertEqual(float(res.progress_8), -0.25)

#     def test_ks5_row_import(self):
#         """Test KS5 data mapping including grades"""
#         row = {
#             'URN': '123456',
#             'TALLPPE_ALEV_1618': '35.5',
#             'TALLPPEGRD_ALEV_1618': 'B-', 
#             'TALLPPEGRD_ACAD_1618': 'SUPP' # Should be cleaned to None
#         }
#         process_ks5_row(row, year=2023)
        
#         res = KS5Performance.objects.get(school=self.school)
#         self.assertEqual(res.a_level_grade, "B-")
#         self.assertEqual(float(res.a_level_points), 35.5)
#         self.assertIsNone(res.academic_grade)

#     def test_row_import_missing_urn_skipped(self):
#         """Ensure rows with unknown URNs are skipped silently"""
#         row = {'URN': '000000', 'PTRWM_EXP': '50'}
#         process_ks2_row(row)
        
#         # Should be 0 because '000000' school doesn't exist in DB
#         self.assertEqual(KS2Performance.objects.filter(school__urn='000000').count(), 0)