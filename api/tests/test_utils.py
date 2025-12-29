import os
import csv
import tempfile
from django.test import TestCase, SimpleTestCase
from django.conf import settings
from api.utils import check_csv_match, read_csv_generator, extract_sector_from_postcode, clean_decimal, clean_int

class CsvUtilsTest(TestCase):
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

    def test_check_csv_match(self):
        # 1. Testing Boolean Flags (The '1' case)
        self.assertTrue(check_csv_match('1', '1'))
        self.assertFalse(check_csv_match('0', '1'))
        
        # 2. Testing Status Strings (The 'Closed' case)
        self.assertTrue(check_csv_match('Closed', 'Closed'))
        self.assertTrue(check_csv_match('closed', 'Closed')) # Case insensitive
        self.assertFalse(check_csv_match('Open', 'Closed'))
        
        # 3. Testing Safety
        self.assertFalse(check_csv_match(None, '1'))
        self.assertFalse(check_csv_match('', 'Closed'))

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

class UtilsCleaningTest(TestCase):
    def test_clean_decimal_happy_path(self):
        """ Test standard valid numbers """
        self.assertEqual(clean_decimal("45.5"), 45.5)
        self.assertEqual(clean_decimal(" 100 "), 100.0) # Trimming
        self.assertEqual(clean_decimal("0.5"), 0.5)

    def test_clean_decimal_formatting(self):
        """ Test stripping special characters common in CSVs """
        self.assertEqual(clean_decimal("45.5%"), 45.5)      # Removes %
        self.assertEqual(clean_decimal("1,250.00"), 1250.0) # Removes comma

    def test_clean_decimal_garbage(self):
        """ Test the 'dirty' government markers return None without crashing """
        self.assertIsNone(clean_decimal("SUPP"))   # Suppressed
        self.assertIsNone(clean_decimal("NE"))     # No Entry
        self.assertIsNone(clean_decimal("NA"))     # Not Available
        self.assertIsNone(clean_decimal("DNS"))    # Did Not Sit
        self.assertIsNone(clean_decimal(""))       # Empty string
        self.assertIsNone(clean_decimal(None))     # Python None

    def test_clean_int_logic(self):
        """ Test integer specific wrapper """
        self.assertEqual(clean_int("1,050"), 1050)
        self.assertEqual(clean_int("1050.0"), 1050) # Floats to Ints
        self.assertIsNone(clean_int("SUPP"))