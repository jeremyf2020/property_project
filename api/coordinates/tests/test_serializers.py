from django.test import TestCase
from api.coordinates.serializers import CoordinatesSerializer

class CoordinatesSerializerTest(TestCase):
    def setUp(self):
        """
        Reusable mock neighbor class to keep tests clean.
        """
        class MockNeighbor:
            def __init__(self, name):
                self.pk = name
                self.name = name
            def __str__(self): return self.name
        self.MockNeighbor = MockNeighbor

    def test_serializer_output_basic_fields(self):
        """
        Test that basic fields (name, lat, long, pop) are serialized correctly.
        """
        class MockCoordinates:
            def __init__(self):
                self.name = "RG1 1"
                self.latitude = 51.45
                self.longitude = -0.97
                self.population = 500
                # Empty neighbors for this test
                class MockManager:
                    def all(self): return []
                self.nearby_sectors = MockManager()

        serializer = CoordinatesSerializer(instance=MockCoordinates())
        data = serializer.data

        self.assertEqual(data['name'], "RG1 1")
        self.assertEqual(data['population'], 500)
        self.assertEqual(data['latitude'], 51.45)

    def test_serializer_nearby_sectors_relationship(self):
        """
        Test specifically that the nearby_sectors relationship is 
        serialized as a list of primary keys (strings).
        """
        class MockCoordinatesWithNeighbors:
            def __init__(self, neighbor_class):
                self.name = "RG1 1"
                self.latitude = 51.45
                self.longitude = -0.97
                self.population = 500
                
                class MockManager:
                    def all(self): 
                        return [neighbor_class("RG1 2"), neighbor_class("RG1 3")]
                self.nearby_sectors = MockManager()

        obj = MockCoordinatesWithNeighbors(self.MockNeighbor)
        serializer = CoordinatesSerializer(instance=obj)
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