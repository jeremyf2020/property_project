from django.test import TestCase
from api.coordinates.models import Coordinates
from api.crimes.models import CrimeCategory, SectorCrimeStat

class CrimeModelTest(TestCase):
    def setUp(self):
        # Mock a sector for the stats to link to
        self.sector = Coordinates.objects.create(
            name="RG1 1", 
            latitude=51.45, 
            longitude=-0.97
        )

    def test_create_crime_category(self):
        """Test that a crime category can be created."""
        category = CrimeCategory.objects.create(name="Burglary")
        self.assertEqual(str(category), "Burglary")

    def test_create_sector_crime_stat(self):
        """Test linking a sector to a category with a count."""
        category = CrimeCategory.objects.create(name="Drugs")
        stat = SectorCrimeStat.objects.create(
            sector=self.sector,
            category=category,
            count=42
        )
        self.assertEqual(stat.count, 42)
        self.assertEqual(stat.sector.name, "RG1 1")
        self.assertEqual(stat.category.name, "Drugs")