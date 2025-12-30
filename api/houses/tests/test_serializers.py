from rest_framework.test import APITestCase
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from api.houses.models import HouseSaleRecord, HouseAddress, HouseFeatures
from api.houses.serializers import HouseSaleSerializer
from api.coordinates.models import Coordinates

class HouseSaleSerializerTest(APITestCase):
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

    def test_update_house_sale_address(self):
        """Test that updating a sale links it to the correct address"""
        # 1. Create an initial sale with "Old Street"
        url = reverse('house-sale-detail', args=[self.sale_record.unique_id])
        
        updated_data = {
            "price_paid": 600000,
            # expect: change the address from "Test Street" to "Corrected Street"
            "address": {
                "saon": "Flat 1",
                "paon": "10",
                "street": "Corrected Street", # <--- The change
                "town": "Reading",
                "postcode": "RG1 1AA"
            },
            "features": {
                "type_code": "F", "tenure_code": "L", 
                "is_new_build": False, "transaction_category": "A"
            }
        }
        
        # 2. Perform patch request
        response = self.client.patch(url, updated_data, format='json')
        
        # --- DEBUGGING: Print the error if it fails ---
        if response.status_code == 400:
            print("\nValidation Error Details:", response.data)
        # ----------------------------------------------

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Verify the link changed
        self.sale_record.refresh_from_db()
        self.assertEqual(self.sale_record.price_paid, 600000)
        self.assertEqual(self.sale_record.address.street, "Corrected Street")
        
        # Verify a NEW address object was created (or found), 
        # distinct from the old one if the old one is still in DB
        self.assertEqual(HouseAddress.objects.count(), 2)

    # [TODO: get_area_crime_stats test to be added later]
    # [TODO: list option not returning area_crime_stats to be tested later]