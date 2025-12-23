import os
import csv

from django.test import TestCase
from api.coordinates.models import Coordinates
from api.coordinates.importer import parse_coordinate_row, loop_csv
from django.conf import settings


class ParserTest(TestCase):
    def test_parse_coordinate_row_keys(self):
        """
        Test that the parser returns correct keys.
        """
        raw_row = {
            'Postcode': 'RG1 1',
            'Latitude': '51.45',
            'Longitude': '-0.97',
            'Population': '500',
            'Nearby Sectors': 'RG1 2, RG1 3'
        }
        
        parsed = parse_coordinate_row(raw_row)
        
        # Check all keys exist
        expected_keys = {'name', 'latitude', 'longitude', 'population', 'raw_neighbors'}
        self.assertEqual(set(parsed.keys()), expected_keys)
        
        # Check specific values
        self.assertEqual(parsed['name'], 'RG1 1')
        self.assertEqual(parsed['raw_neighbors'], ['RG1 2', 'RG1 3'])

    def test_parse_handles_empty_values(self):
        """
        Check that it doesn't crash if optional data is missing.
        """
        raw_row = {'Postcode': 'RG1 1'} # Minimum data
        parsed = parse_coordinate_row(raw_row)
        
        self.assertIsNone(parsed['latitude'])
        self.assertEqual(parsed['population'], 0)
        self.assertEqual(parsed['raw_neighbors'], [])

class ImporterSaveTest(TestCase):
    def setUp(self):
        # Arrange: mock file
        self.filename = "test_save_logic.csv"
        self.data_path = os.path.join(settings.BASE_DIR, 'data', self.filename)
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)

        with open(self.data_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Postcode', 'Latitude', 'Longitude', 'Population', 'Nearby Sectors'])
            writer.writerow(['RG1 1', '51.1', '-0.1', '100', 'RG1 2, RG1 3'])
            writer.writerow(['RG1 2', '51.2', '-0.2', '200', '']) # No neighbors

    def tearDown(self):
        if os.path.exists(self.data_path):
            os.remove(self.data_path)

    def test_save_sectors_and_return_map(self):
        # Act: run loop: save data and return map
        returned_map = loop_csv(self.filename)

        # Assert: check saved data
        self.assertEqual(Coordinates.objects.count(), 2)
        rg1 = Coordinates.objects.get(name="RG1 1")
        self.assertEqual(rg1.population, 100)

        # Assert: Return Value (The Map)
        # Expected: {'RG1 1': ['RG1 2', 'RG1 3']}
        self.assertIn('RG1 1', returned_map)
        self.assertEqual(returned_map['RG1 1'], ['RG1 2', 'RG1 3'])
        
        # RG1 2 should not be in the map because its raw_neighbors was empty
        self.assertNotIn('RG1 2', returned_map)