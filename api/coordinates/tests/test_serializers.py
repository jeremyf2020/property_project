from django.test import TestCase
from api.coordinates.serializers import CoordinatesSerializer
from api.coordinates.models import Coordinates
from api.crimes.models import CrimeCategory, SectorCrimeStat

class CoordinatesSerializerTest(TestCase):
    def setUp(self):
        """ Arrange: create a sector to test with """
        self.coordinate = Coordinates.objects.create(
            name="RG1 1",
            latitude=51.45,
            longitude=-0.97,
            population=1000
        )

    def test_serializer_output_basic_fields(self):
        """
        Test that basic fields (name, lat, long, pop) are serialized correctly.
        """
        serializer = CoordinatesSerializer(instance=self.coordinate)
        data = serializer.data

        self.assertEqual(data['name'], "RG1 1")
        self.assertEqual(data['population'], 1000)
        self.assertEqual(data['latitude'], 51.45)

    def test_serializer_nearby_sectors_relationship(self):
        """
        Test that the nearby_sectors relationship is serialized as a 
        list of primary keys (strings).
        """
        # Create neighbor instances
        neighbor1 = Coordinates.objects.create(name="RG1 2")
        neighbor2 = Coordinates.objects.create(name="RG1 3")
        
        # Add them to the relationship
        self.coordinate.nearby_sectors.add(neighbor1, neighbor2)

        serializer = CoordinatesSerializer(instance=self.coordinate)
        data = serializer.data

        # Verify the list contains the expected primary keys
        self.assertEqual(len(data['nearby_sectors']), 2)
        self.assertIn("RG1 2", data['nearby_sectors'])
        self.assertIn("RG1 3", data['nearby_sectors'])

    def test_serializer_validation_fails_for_bad_postcode(self):
        """
        Test that the serializer respects the model's RegexValidator.
        """
        invalid_data = {
            'name': 'NOT-A-POSTCODE',
            'latitude': 51.0,
            'longitude': 0.0,
            'population': 10
        }
        serializer = CoordinatesSerializer(data=invalid_data)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('name', serializer.errors)

    def test_coordinates_serializer_includes_total_crimes(self):
        """
        Verify that total_crimes correctly aggregates related SectorCrimeStat counts.
        """
        # Arrange: create categories and link stats to our existing coordinate
        cat1 = CrimeCategory.objects.create(name="Theft")
        cat2 = CrimeCategory.objects.create(name="Drugs")

        SectorCrimeStat.objects.create(sector=self.coordinate, category=cat1, count=10)
        SectorCrimeStat.objects.create(sector=self.coordinate, category=cat2, count=5)

        # Act: serialize the sector
        serializer = CoordinatesSerializer(instance=self.coordinate)
        
        # Assert: total_crimes should be 15
        self.assertEqual(serializer.data['total_crimes'], 15)
        self.assertEqual(len(serializer.data['crime_stats']), 2)