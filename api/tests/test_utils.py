import os
import csv
import tempfile
from django.test import TestCase
from django.conf import settings
from api.utils import read_csv_generator

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
        """
        user can get the data from default folder correctly
        """
        # ACT: Pass ONLY the filename
        rows = list(read_csv_generator(self.filename))

        # ASSERT
        self.assertEqual(rows[0]['Postcode'], 'RG1 1')

    def test_raises_error_on_wrong_path(self):
        """
        error if user can input invalid path
        """
        # arrange wrong path
        wrong_path = os.path.join(self.data_dir, 'wrong_path.csv')

        # assert it fails if act on wrong path
        with self.assertRaises(FileNotFoundError):
            list(read_csv_generator(wrong_path))