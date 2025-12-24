from django.test import TestCase
from api.coordinates.models import Coordinates
from api.crimes.models import CrimeCategory, SectorCrimeStat
from api.crimes.serializers import SectorCrimeStatSerializer

class CrimeSerializerTest(TestCase):
    def setUp(self):
        # Arrange: mock data
        self.sector = Coordinates.objects.create(name="RG1 1")
        self.category = CrimeCategory.objects.create(name="Burglary")
        self.stat = SectorCrimeStat.objects.create(
            sector=self.sector,
            category=self.category,
            count=10
        )

    def test_sector_crime_stat_serializer(self):
        """Test that the crime stat serializes the category name and count."""
        # Act: return serialized data
        serializer = SectorCrimeStatSerializer(instance=self.stat)
        data = serializer.data
        
        # Assert: verify serialized output
        self.assertEqual(data['category'], "Burglary")
        self.assertEqual(data['count'], 10)