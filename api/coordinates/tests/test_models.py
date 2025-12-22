from django.test import TestCase
from api.coordinates.models import Coordinates
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

class CoordinatesTest(TestCase):
    def test_coordinates_creation(self):
        """
        Test that we can save and retrieve data correctly
        """
        sector = Coordinates.objects.create(
            name="RG1 1",
            latitude=51.4569,
            longitude=-0.973118,
        )
        
        # Verify Data Saved
        self.assertEqual(Coordinates.objects.count(), 1)
        # Verify __str__ method return postcode sector as name
        self.assertEqual(str(sector), "RG1 1")

    
    def test_validation_fails_on_bad_input(self):
        """
        Test that model validation catches issues.
        """
        sector = Coordinates(
            name="RG1 1",
            latitude="22-Dec-2025",
            longitude="-0.973118"
        )
        
        with self.assertRaises(ValidationError):
            sector.full_clean()

    def test_duplicate_primary_key_fails(self):
        """
        'name' is primary_key. 
        Trying to create "RG1 1" twice should crash.
        """
        Coordinates.objects.create(name="RG1 1")
        
        with self.assertRaises(IntegrityError):
            Coordinates.objects.create(name="RG1 1")

    def test_nearby_sectors_relationship(self):
        """
        Many-to-Many Relationship.
        linking 'RG1 1' to 'RG1 2'
        """
        # Arrange: Create two sectors
        rg1_1 = Coordinates.objects.create(name="RG1 1")
        rg1_2 = Coordinates.objects.create(name="RG1 2")

        # Act: Link them
        rg1_1.nearby_sectors.add(rg1_2)

        # Assert 1: Check the link exists
        self.assertIn(rg1_2, rg1_1.nearby_sectors.all())
        # Assert 2: as symmetrical=False, RG1 2 should NOT automatically know about RG1 1
        self.assertNotIn(rg1_1, rg1_2.nearby_sectors.all())

    def test_name_validation(self):
        """
        Test that valid names pass and invalid names fail.
        """
        # Valid Examples (Should pass)
        valid_sectors = ["RG1 1", "W1A 0", "EC1A 1", "B33 8"]
        for name in valid_sectors:
            sector = Coordinates(name=name)
            try:
                sector.full_clean()  # Should not raise error
            except ValidationError:
                self.fail(f"Valid postcode sector '{name}' failed validation!")

        # Invalid Examples (Should fail)
        invalid_sectors = [
            "HELLO",      # No digits
            "RG1",        # Missing sector digit
            "RG1 1AA",    # Full postcode (too long)
            "rg1 1",      # Lowercase (regex expects uppercase)
            "123 4",      # Starts with number
        ]
        
        for name in invalid_sectors:
            sector = Coordinates(name=name)
            with self.assertRaises(ValidationError, msg=f"Invalid '{name}' should have failed"):
                sector.full_clean()