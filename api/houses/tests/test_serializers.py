from django.test import TestCase
from api.houses.models import HouseSaleRecord, HouseAddress, HouseFeatures
from api.houses.serializers import HouseSaleSerializer
from api.coordinates.models import Coordinates

class HouseSaleSerializerTest(TestCase):
    def setUp(self):
        self.correndiate = Coordinates.objects.create(name="RG1 1")
        # 1. Create dependencies
        self.address = HouseAddress.objects.create(
            saon="Flat 1",
            paon="10",
            street="Test Street",
            locality="Locality",
            postcode="RG1 1AA"
        )
        
        self.features = HouseFeatures.objects.create(
            type_code="F",
            tenure_code="L",
            is_new_build=False,
            transaction_category="A"
        )
        
        # 2. Create the main record
        self.sale_record = HouseSaleRecord.objects.create(
            unique_id="TEST-UUID-001",
            price_paid=250000,
            deed_date="2024-03-15",
            address=self.address,
            features=self.features,
        )

    def test_contains_expected_fields(self):
        # Initialize serializer
        serializer = HouseSaleSerializer(instance=self.sale_record)
        data = serializer.data

        # 1. Assert specific fields exist
        self.assertEqual(data['unique_id'], "TEST-UUID-001")
        self.assertEqual(data['price_paid'], '250000')
        self.assertEqual(data['deed_date'], "2024-03-15")
        
        # 2. Assert Nested Address Data
        self.assertEqual(data['address']['paon'], "10")
        self.assertEqual(data['address']['street'], "Test Street")
        
        # 3. Assert Nested Features Data
        self.assertEqual(data['features']['type_code'], "F")
        self.assertEqual(data['features']['is_new_build'], False)
        
        # 4. Assert derived/human-readable fields (Optional but good practice)
        self.assertEqual(data['features']['property_type_display'], 'Flats/Maisonettes')