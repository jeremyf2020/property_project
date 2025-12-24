import os
import csv
from django.test import TestCase
from django.conf import settings
from api.coordinates.models import Coordinates
from api.crimes.models import SectorCrimeStat, CrimeCategory
from api.crimes.importer import run_crime_import

class CrimeImporterTest(TestCase):
    def setUp(self):
        # mock the coordinate needed for the link
        Coordinates.objects.create(name="RG1 1")
        
        # mock CSV file
        self.filename = "test_crime_stats.csv"
        self.data_path = os.path.join(settings.BASE_DIR, 'data', self.filename)
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)

        with open(self.data_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Match your actual CSV headers
            writer.writerow(['postcode_sector', 'Burglary', 'Drugs', 'total_crimes'])
            writer.writerow(['RG1 1', '38', '29', '67'])

    def tearDown(self):
        if os.path.exists(self.data_path):
            os.remove(self.data_path)

    def test_run_crime_import_populates_db(self):
        """Verify the importer creates categories and stats from CSV."""
        run_crime_import(self.filename)

        # Check categories created
        self.assertTrue(CrimeCategory.objects.filter(name="Burglary").exists())
        self.assertTrue(CrimeCategory.objects.filter(name="Drugs").exists())

        # Check stats linked correctly
        stat = SectorCrimeStat.objects.get(sector_id="RG1 1", category_id="Burglary")
        self.assertEqual(stat.count, 38)