from django.test import TestCase
from unittest.mock import patch
from api.coordinates.models import Coordinates
from api.schools.models import School, KS2Performance, KS4Performance, KS5Performance
from api.schools.importer import (
    process_school_row,
    process_ks2_row,
    process_ks4_row,
    process_ks5_row,
    run_school_base_import,
    run_ks2_import_wrapper,
    run_ks4_import_wrapper
)

class SchoolImporterRowTest(TestCase):
    def setUp(self):
        # Create a Coordinates sector to link to
        self.sector_1_1 = Coordinates.objects.create(name='RG1 1')
        self.sector_4_7 = Coordinates.objects.create(name='RG4 7')
        self.sector_6_1 = Coordinates.objects.create(name='RG6 1')

    def test_process_school_row_standard(self):
        """
        Test a standard active primary school import.
        Verifies:
        - Boolean flags map '1' -> True
        - Status 'Open' -> is_closed=False
        - Basic fields (Name, Address) map correctly
        """
        row = {
            'URN': '109776',
            'SCHNAME': 'Alfred Sutton Primary School',
            'STREET': '148 Wokingham Road',
            'LOCALITY': '',
            'ADDRESS3': '', 
            'POSTCODE': 'RG6 1JR',
            'SCHSTATUS': 'Open',       # Should mean is_closed = False
            'SCHOOLTYPE': 'Community school',
            'GENDER': 'Mixed',
            'ISPRIMARY': '1',          # Should mean is_primary = True
            'ISSECONDARY': '0',
            'ISPOST16': '0',
            'AGELOW': '3',
            'AGEHIGH': '11'
        }
        
        # Act
        process_school_row(row)
        
        # Assert
        school = School.objects.get(urn='109776')
        self.assertEqual(school.name, 'Alfred Sutton Primary School')
        self.assertEqual(school.street, '148 Wokingham Road')
        
        # Verify Flags
        self.assertTrue(school.is_primary)
        self.assertFalse(school.is_secondary)
        self.assertFalse(school.is_post16)
        
        # Verify Status
        self.assertFalse(school.is_closed) # 'Open' != 'Closed'

    def test_process_school_row_closed_and_secondary(self):
        """
        Test a closed secondary school.
        Verifies:
        - Status 'Closed' -> is_closed=True
        - Secondary flag '1' -> is_secondary=True
        """
        row = {
            'URN': '110112',
            'SCHNAME': 'Hemdean House School',
            'POSTCODE': 'RG4 7SD',
            'SCHSTATUS': 'Closed',     # <--- Target Match
            'ISPRIMARY': '0',
            'ISSECONDARY': '1',        # <--- Target Match
            'ISPOST16': '0',
            'AGELOW': '11',
            'AGEHIGH': '16'
        }
        
        process_school_row(row)
        
        school = School.objects.get(urn='110112')
        self.assertTrue(school.is_closed)
        self.assertTrue(school.is_secondary)
        self.assertFalse(school.is_primary)

    def test_process_school_row_updates_existing(self):
        """
        Test that if a school exists, it updates the data instead of crashing.
        """
        # Arrange: Create initial school
        School.objects.create(
            urn='100001', 
            name="Old Name", 
            postcode='RG1 1AA', 
        )
        
        # Act: Import new data for same URN
        row = {
            'URN': '100001',
            'SCHNAME': 'New Name',
            'POSTCODE': 'RG1 1AA',
            'SCHSTATUS': 'Open',
            'ISPRIMARY': '1'
        }
        process_school_row(row)
        
        # Assert: Verify update happened
        school = School.objects.get(urn='100001')
        self.assertEqual(school.name, 'New Name')
        self.assertEqual(School.objects.count(), 1) # Should still be 1 school

    def test_process_school_row_skips_missing_urn(self):
        """
        Ensure rows without a URN are ignored.
        """
        row = {
            'URN': '', # Empty
            'SCHNAME': 'Ghost School'
        }
        process_school_row(row)
        
        self.assertEqual(School.objects.count(), 0)

class KS2ImporterTest(TestCase):
    def setUp(self):
        # Arrange: Mock a school to link KS2 data to
        self.sector = Coordinates.objects.create(name="RG1 1")
        self.school = School.objects.create(
            urn="100100", 
            name="Test Primary", 
            postcode="RG1 1AA",
            postcode_sector=self.sector
        )

    def test_process_ks2_row_success(self):
        """
        Happy Path: Import standard scores and percentages.
        """
        row = {
            'URN': '100100',
            'PTRWM_EXP': '65.5%',   # % Meeting Expected Standard
            'READ_AVERAGE': '105',  # Reading Score
            'MAT_AVERAGE': '104'    # Maths Score
        }
        
        process_ks2_row(row, year=2024)
        
        # Assert imported correctly
        result = KS2Performance.objects.get(school=self.school, academic_year=2024)
        self.assertEqual(float(result.pct_meeting_expected), 65.5)
        self.assertEqual(float(result.reading_score), 105.0)
        self.assertEqual(float(result.maths_score), 104.0)

    def test_process_ks2_row_cleans_suppressed_data(self):
        """
        Edge Case: 'SUPP' (Suppressed) or 'NE' (No Entry) should become None.
        """
        row = {
            'URN': '100100',
            'PTRWM_EXP': 'SUPP', 
            'READ_AVERAGE': 'NE',
            'MAT_AVERAGE': '' 
        }
        
        process_ks2_row(row, year=2024)
        
        # Assert imported correctly
        result = KS2Performance.objects.get(school=self.school)
        self.assertIsNone(result.pct_meeting_expected)
        self.assertIsNone(result.reading_score)
        self.assertIsNone(result.maths_score)

    def test_process_ks2_row_skips_unknown_school(self):
        """
        Safety: If URN doesn't exist, do nothing (don't crash).
        """
        row = {'URN': '999999', 'PTRWM_EXP': '100'}
        
        process_ks2_row(row, year=2024)
        
        # Ensure no orphan records created
        self.assertEqual(KS2Performance.objects.count(), 0)

    def test_process_ks2_row_updates_existing(self):
        """
        Idempotency: Re-running the import updates data, doesn't duplicate.
        """
        # Arrange: Create initial record
        KS2Performance.objects.create(
            school=self.school, 
            academic_year=2024, 
            reading_score=100
        )
        
        # Act: Import new data (Improved score)
        row = {
            'URN': '100100', 
            'READ_AVERAGE': '110'
        }
        process_ks2_row(row, year=2024)
        
        # Assert updated correctly
        result = KS2Performance.objects.get(school=self.school)
        self.assertEqual(float(result.reading_score), 110.0)
        self.assertEqual(KS2Performance.objects.count(), 1)

class KS4ImporterTest(TestCase):
    def setUp(self):
        self.sector = Coordinates.objects.create(name="RG1 1")
        self.school = School.objects.create(
            urn="100200", 
            name="Test Secondary", 
            postcode="RG1 1AA",
            postcode_sector=self.sector
        )

    def test_process_ks4_row_success(self):
        """
        Happy Path: Import Progress 8 (negative allowed) and Attainment 8.
        """
        row = {
            'URN': '100200',
            'P8MEA': '-0.25',   # Progress 8 (Negative is valid)
            'ATT8SCR': '45.2'   # Attainment 8
        }
        
        process_ks4_row(row, year=2024)
        
        # Assert imported correctly
        result = KS4Performance.objects.get(school=self.school, academic_year=2024)
        self.assertEqual(float(result.progress_8), -0.25)
        self.assertEqual(float(result.attainment_8), 45.2)

    def test_process_ks4_row_cleans_garbage(self):
        """
        Edge Case: 'SUPP' (Suppressed), 'NE', or empty strings become None.
        """
        row = {
            'URN': '100200',
            'P8MEA': 'SUPP', 
            'ATT8SCR': '' 
        }
        
        process_ks4_row(row, year=2024)
        
        # Assert imported correctly
        result = KS4Performance.objects.get(school=self.school)
        self.assertIsNone(result.progress_8)
        self.assertIsNone(result.attainment_8)

    def test_process_ks4_row_skips_unknown_school(self):
        """
        Safety: Unknown URNs are ignored silently.
        """
        row = {'URN': '999999', 'P8MEA': '0.5'}
        process_ks4_row(row, year=2024)
        
        self.assertEqual(KS4Performance.objects.count(), 0)

    def test_process_ks4_row_updates_existing(self):
        """
        Idempotency: Re-running updates the existing record.
        """
        # Arrange: Create initial
        KS4Performance.objects.create(
            school=self.school, 
            academic_year=2024, 
            progress_8=0.1
        )
        
        # Act: Update with new data
        row = {
            'URN': '100200', 
            'P8MEA': '0.5'
        }
        process_ks4_row(row, year=2024)
        
        # Assert updated correctly
        result = KS4Performance.objects.get(school=self.school)
        self.assertEqual(float(result.progress_8), 0.5)
        self.assertEqual(KS4Performance.objects.count(), 1)

class KS5ImporterTest(TestCase):
    def setUp(self):
        self.sector = Coordinates.objects.create(name="RG1 1")
        self.school = School.objects.create(
            urn="100300", 
            name="Test College", 
            postcode="RG1 1AA",
            postcode_sector=self.sector
        )

    def test_process_ks5_row_success(self):
        """
        Happy Path: Import Points (decimal) and Grades (string).
        """
        row = {
            'URN': '100300',
            # A-Level
            'TALLPPE_ALEV_1618': '35.50',
            'TALLPPEGRD_ALEV_1618': 'B-', 
            # Academic
            'TALLPPE_ACAD_1618': '36.00',
            'TALLPPEGRD_ACAD_1618': 'B'
        }
        
        process_ks5_row(row, year=2024)
        
        # Verify
        result = KS5Performance.objects.get(school=self.school, academic_year=2024)
        
        # Check Points
        self.assertEqual(float(result.a_level_points), 35.5)
        self.assertEqual(float(result.academic_points), 36.0)
        
        # Check Grades (Should remain strings)
        self.assertEqual(result.a_level_grade, "B-")
        self.assertEqual(result.academic_grade, "B")

    def test_process_ks5_row_cleans_grades(self):
        """
        Edge Case: 'SUPP', 'NE', 'NA' in Grade columns should become None.
        """
        row = {
            'URN': '100300',
            'TALLPPE_ALEV_1618': 'SUPP', 
            'TALLPPEGRD_ALEV_1618': 'SUPP', # Should be None
            'TALLPPEGRD_ACAD_1618': 'NE'    # Should be None
        }
        
        process_ks5_row(row, year=2024)
        
        result = KS5Performance.objects.get(school=self.school)
        self.assertIsNone(result.a_level_points)
        self.assertIsNone(result.a_level_grade)
        self.assertIsNone(result.academic_grade)

    def test_process_ks5_row_skips_unknown_school(self):
        """
        Safety: Unknown URNs are ignored.
        """
        row = {'URN': '999999', 'TALLPPE_ALEV_1618': '30'}
        process_ks5_row(row, year=2024)
        self.assertEqual(KS5Performance.objects.count(), 0)

class ImporterWrapperParameterTest(TestCase):
    @patch('api.schools.importer.read_csv_generator')
    @patch('api.schools.importer.process_ks2_row')
    def test_ks2_wrapper_accepts_custom_year(self, mock_process, mock_reader):
        """
        Verify we can import old data (e.g. 2019) by passing the parameter.
        """
        # Mock CSV data
        mock_reader.return_value = [{'URN': '1'}]
        
        # Call with custom year
        run_ks2_import_wrapper("data.csv", year=2019)
        
        # Verify the year 2019 was passed to the processor
        mock_process.assert_called_once_with({'URN': '1'}, year=2019)

    @patch('api.schools.importer.read_csv_generator')
    @patch('api.schools.importer.process_ks4_row')
    def test_ks4_wrapper_defaults_to_2024(self, mock_process, mock_reader):
        """
        Verify it defaults to 2024 if no year is provided.
        """
        mock_reader.return_value = [{'URN': '1'}]
        
        run_ks4_import_wrapper("data.csv")
        
        # Verify default year
        mock_process.assert_called_once_with({'URN': '1'}, year=2024)

    @patch('api.schools.importer.read_csv_generator')
    @patch('api.schools.importer.process_school_row')
    def test_school_base_wrapper_accepts_year(self, mock_process, mock_reader):
        """
        Verify school info wrapper accepts year parameter for updates.
        """
        mock_reader.return_value = [{'URN': '1'}]
        
        # Run with a future year
        run_school_base_import("dummy.csv", year=2025)
        
        # Assert it was passed down
        mock_process.assert_called_once_with({'URN': '1'}, year=2025)
