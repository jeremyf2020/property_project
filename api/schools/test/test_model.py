from django.test import TestCase
from django.core.exceptions import ValidationError
from api.coordinates.models import Coordinates
from api.schools.models import School

class SchoolCoreLogicTest(TestCase):
    def setUp(self):
        # 1. Prepare the Map (The Parent)
        self.sector = Coordinates.objects.create(name="RG1 1")

    # --- MODEL TESTS ---
    def test_school_auto_links_to_sector(self):
        """
        Test that saving a School with 'RG1 1AA' automatically finds 'RG1 1' sector.
        """
        school = School(
            urn="100123",
            name="TDD Academy",
            postcode="RG1 1AA"
        )
        school.save()
        
        # Expectation: The relationship is set automatically
        self.assertEqual(school.postcode_sector, self.sector)

    def test_school_validation_error_missing_sector(self):
        """
        Test that we cannot save a school if its sector doesn't exist.
        """
        school = School(
            urn="999999",
            name="Lost School",
            postcode="ZZ99 9ZZ" # Sector 'ZZ99 9' does not exist
        )
        # Expectation: save() raises ValidationError
        with self.assertRaises(ValidationError):
            school.save()

    # --- IMPORTER LOGIC TESTS ---
    def test_clean_value_sanitization(self):
        """
        Test that CSV garbage is converted to None.
        """
        self.assertIsNone(clean_value("SUPP"))
        self.assertIsNone(clean_value("NE"))
        self.assertIsNone(clean_value(""))
        self.assertEqual(clean_value("Reading School"), "Reading School")
        self.assertEqual(clean_value("  123  "), "123") # Trimming

    def test_process_row_logic(self):
        """
        Test processing a raw CSV row dictionary.
        """
        row = {
            'URN': '100123',
            'SCHNAME': 'Reading Importer School',
            'POSTCODE': 'RG1 1AA', # Valid Sector exists
            'LANAME': 'Reading',
            'SCHSTATUS': 'Open'
        }
        
        # Run the function
        school, created = process_school_row(row)
        
        # Expectation: School is created and linked
        self.assertTrue(created)
        self.assertEqual(school.name, 'Reading Importer School')
        self.assertEqual(school.postcode_sector.name, 'RG1 1')