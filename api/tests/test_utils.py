import os
import csv
import tempfile
from django.test import TestCase, SimpleTestCase
from django.conf import settings
from api.utils import read_csv_generator, extract_sector_from_postcode

class UtilsTest(TestCase):
    def setUp(self):
        # Arrange file path 
        self.data_dir = os.path.join(settings.BASE_DIR, 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.filename = "test_sectors.csv"
        self.full_path = os.path.join(self.data_dir, self.filename)
        
        with open(self.full_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Postcode', 'Nearby Sectors'])
            writer.writerow(['RG1 1', 'RG1 8, RG1 2, RG1 7, RG1 4, RG1 3, RG1 6, RG4 5, RG2 0, RG30 9, RG4 8'])

    def tearDown(self):
        # Cleanup temp path, but keep data path
        if os.path.exists(self.full_path):
            os.remove(self.full_path)

    def test_reads_from_default_data_folder(self):
        """ user can get the data from default folder correctly """
        # ACT: Pass ONLY the filename
        rows = list(read_csv_generator(self.filename))

        # ASSERT
        self.assertEqual(rows[0]['Postcode'], 'RG1 1')

    def test_raises_error_on_wrong_path(self):
        """ error if user can input invalid path """
        # arrange wrong path
        wrong_path = os.path.join(self.data_dir, 'wrong_path.csv')

        # assert it fails if act on wrong path
        with self.assertRaises(FileNotFoundError):
            list(read_csv_generator(wrong_path))

class PostcodeUtilsTest(SimpleTestCase):
    def test_extract_standard_format(self):
        """ test standard postcode formats "RG1 1AF" -> "RG1 1" """
        self.assertEqual(extract_sector_from_postcode("RG1 1AF"), "RG1 1")
        self.assertEqual(extract_sector_from_postcode("SW1A 1AA"), "SW1A 1")
        self.assertEqual(extract_sector_from_postcode("B33 8TH"), "B33 8")

    def test_extract_handles_lowercase_and_spacing(self):
        """ test it handles lowercase and extra spaces """
        # "rg1 1af" -> "RG1 1"
        self.assertEqual(extract_sector_from_postcode("rg1 1af"), "RG1 1")
        # "  RG1 1AF  " -> "RG1 1"
        self.assertEqual(extract_sector_from_postcode("  RG1 1AF  "), "RG1 1")

    def test_invalid_postcodes_return_none(self):
        """ test various invalid postcodes return None """
        # Missing space
        self.assertIsNone(extract_sector_from_postcode("RG11AF")) 
        # Not a postcode
        self.assertIsNone(extract_sector_from_postcode("NOT A CODE"))
        # Partial postcode
        self.assertIsNone(extract_sector_from_postcode("RG1"))
        # Empty
        self.assertIsNone(extract_sector_from_postcode(""))
        self.assertIsNone(extract_sector_from_postcode(None))