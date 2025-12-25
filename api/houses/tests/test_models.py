from django.test import TestCase
from api.coordinates.models import Coordinates
from api.houses.models import HouseFeatures, Address, HouseSale
from datetime import date
from django.core.exceptions import ValidationError

class HouseModuleTest(TestCase):
    def setUp(self):
        """ 
        Arrange: mock object for tests
        """
        # mock Coordinate for Address FK
        self.coordinate = Coordinates.objects.create(name="RG30 4")
        self.coord_RG1_1 = Coordinates.objects.create(name="RG1 1")
        self.coord_RG2_2 = Coordinates.objects.create(name="RG2 2")

        # mock Features: "Detached - Freehold (Not New Build)
        self.features = HouseFeatures.objects.create(
            type_code='D',
            tenure_code='F',
            is_new_build=False
        )

        # mock address
        self.address = Address.objects.create(
            saon="FLAT 6",
            paon="RED KITE HOUSE, 96",
            street="DEVERON DRIVE",
            locality="TILEHURST",
            postcode="RG30 4ET",
        )

    def test_features_creation(self):
        """ Test that HouseFeatures __str__ method works as expected."""
        self.assertEqual(str(self.features), "Detached - Freehold (Not New Build)")

        # test 2: Semi-Detached - Leasehold (New Build)
        features_S_L_N = HouseFeatures.objects.create(
            type_code='S', tenure_code='L', is_new_build=True
        )
        self.assertEqual(str(features_S_L_N), "Semi-Detached - Leasehold (New Build)")

        # test 3: Terraced - Freehold (Not New Build)
        features_T_F_F = HouseFeatures.objects.create(
            type_code='T', tenure_code='F', is_new_build=False
        )
        self.assertEqual(str(features_T_F_F), "Terraced - Freehold (Not New Build)")

    def test_address_auto_assigns_postcode_sector(self):
        """ Test that Address auto-assigns postcode_sector based on postcode."""
        addr = Address.objects.create(
            paon="15", street="Baker St", postcode="RG2 2AB"
        )
        self.assertEqual(addr.postcode_sector, self.coord_RG2_2)

    def test_address_creation(self):
        """ Test that Address __str__ method works as expected."""
        addr = Address.objects.create(
            paon="10", street="Station Rd", postcode="RG1 1AF"
        )
        self.assertEqual(str(addr), "10 Station Rd, RG1 1AF")

        addr_with_saon = Address.objects.create(
            paon="20", saon="Flat 2", street="High St", postcode="RG2 2BB"
        )
        self.assertEqual(str(addr_with_saon), "Flat 2, 20 High St, RG2 2BB")

        # FULL address
        self.assertEqual(str(self.address), "FLAT 6, RED KITE HOUSE, 96 DEVERON DRIVE, TILEHURST, RG30 4ET")

    def test_create_address_linked_to_coordinate(self):
        addr = Address.objects.create(
            paon="10", street="Station Rd", postcode="RG1 1AF", postcode_sector=self.coord_RG1_1
        )
        self.assertEqual(addr.postcode_sector.name, "RG1 1")


    def test_create_house_sale(self):
        """Test that can create a sale linked to an address."""
        # Act: Create HouseSale record
        sale = HouseSale.objects.create(
            unique_id="31C68071-BDF4-FEE3-E063-4804A8C04F37",
            price_paid=205000.00,
            deed_date=date(2025, 1, 15),
            address=self.address,
            features=self.features
        )

        # Assertions
        self.assertEqual(sale.price_paid, 205000.00)
        self.assertEqual(sale.address.postcode, "RG30 4ET")
        self.assertEqual(sale.address.postcode_sector.name, "RG30 4")
        # Check reverse relationship: Address should know about its sales
        self.assertEqual(self.address.sales.count(), 1)

    def test_multiple_sales_for_same_house(self):
        """Test that one house can have history (multiple sales)."""
        # Sale 1 (2025-01-01)
        HouseSale.objects.create(
            unique_id="SALE-1",
            price_paid=100000,
            deed_date=date(2025, 1, 1),
            address=self.address,
            features=self.features
        )
        # Sale 2 (2025-12-01)
        HouseSale.objects.create(
            unique_id="SALE-2",
            price_paid=450000,
            deed_date=date(2025, 12, 1),
            address=self.address,
            features=self.features
        )

        # Retrieve address and check history
        sales = self.address.sales.all().order_by('deed_date')
        self.assertEqual(sales.count(), 2)
        self.assertEqual(sales.first().price_paid, 100000)
        self.assertEqual(sales.last().price_paid, 450000)

    def test_address_validation_fails_without_sector(self):
        """Test that creating an address fails if the sector doesn't exist."""
        with self.assertRaises(ValidationError):
            Address.objects.create(
                paon="99",
                street="Nowhere St",
                postcode="ZZ99 9ZZ" # "ZZ99 9" doesn't exist in Coordinates
            )