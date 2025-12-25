from django.test import TestCase
from django.core.exceptions import ValidationError
from api.coordinates.models import Coordinates
from api.crimes import models
from api.schools.models import School

class SchoolCoreLogicTest(TestCase):
    def setUp(self):
        # Arrange: mock sector for auto assignment
        self.sector = Coordinates.objects.create(name="RG4 7")
        # sample school data instance
        self.school_data = {
            'name':"Hemdean House School",
            'street':"Hemdean Road",
            'locality':"Caversham",
            'address3':"", 
            'postcode':"RG4 7SD",
            'school_type':"Other independent school",
            'is_closed':"Closed",
            'gender':"Mixed",
            'is_primary': "1",
            'is_secondary': "0",
            'is_post16': "0",
            'minimum_age': "4",
            'maximum_age': "18",
        }

    def test_school_creation_basic(self):
        """
        Test that we can create a School instance with basic data.
        """
        school = School.objects.create(
            name=self.school_data['name'],
            street=self.school_data['street'],
            locality=self.school_data['locality'],
            address3=self.school_data['address3'],
            postcode=self.school_data['postcode'],
            school_type=self.school_data['school_type'],
            is_closed=(self.school_data['is_closed'] == "Closed"),
            gender=self.school_data['gender'],
            is_primary=bool(int(self.school_data['is_primary'])),
            is_secondary=bool(int(self.school_data['is_secondary'])),
            is_post16=bool(int(self.school_data['is_post16'])),
            minimum_age=int(self.school_data['minimum_age']),
            maximum_age=int(self.school_data['maximum_age']),
        )
        school.save() # Ensure save() is called to trigger sector assignment

        self.assertEqual(School.objects.count(), 1)

        self.assertEqual(school.name, self.school_data["name"])

        # Location
        self.assertEqual(school.street, self.school_data["street"])
        self.assertEqual(school.locality, self.school_data["locality"])
        self.assertEqual(school.postcode, self.school_data["postcode"])

        # Details
        self.assertTrue(school.is_closed, "School should be marked as closed")
        self.assertEqual(school.school_type, self.school_data["school_type"])
        self.assertEqual(school.gender, self.school_data["gender"])
       
        # Phase Flags
        self.assertTrue(school.is_primary)
        self.assertFalse(school.is_secondary)     
        self.assertFalse(school.is_post16)

        # Age Range 
        self.assertEqual(school.minimum_age, 4)
        self.assertEqual(school.maximum_age, 18)
        
        # The Link
        self.assertEqual(school.postcode_sector, self.sector)

    def test_school_str_method(self):
        """
        Test that School __str__ method works as expected.
        """
        school = School.objects.create(
            name="St. Mary's Primary School",
            postcode="RG4 7SD",
            postcode_sector=self.sector
        )
        self.assertEqual(str(school), "St. Mary's Primary School")

    def test_school_phase_property(self):
        """
        Test that the 'phase' property returns correct string.
        """
        # Primary only
        school_primary = School.objects.create(
            name="Primary School",
            postcode="RG4 7SD",
            postcode_sector=self.sector,
            is_primary=True,
            is_secondary=False,
            is_post16=False
        )
        self.assertEqual(school_primary.phase, "Primary")

        # Secondary only
        school_secondary = School.objects.create(
            name="Secondary School",
            postcode="RG4 7SD",
            postcode_sector=self.sector,
            is_primary=False,
            is_secondary=True,
            is_post16=False
        )
        self.assertEqual(school_secondary.phase, "Secondary")

        # All-through
        school_all_through = School.objects.create(
            name="All-through School",
            postcode="RG4 7SD",
            postcode_sector=self.sector,
            is_primary=True,
            is_secondary=True,
            is_post16=False
        )
        self.assertEqual(school_all_through.phase, "All-through")

    def test_school_age_range_str_property(self):
        """
        Test that the 'age_range_str' property returns correct string.
        """
        school = School.objects.create(
            name="Age Range School",
            postcode="RG4 7SD",
            postcode_sector=self.sector,
            minimum_age=5,
            maximum_age=11
        )
        self.assertEqual(school.age_range_str, "5-11")

    def test_school_auto_links_to_sector(self):
        """
        Test that saving a School with 'RG4 7SD' automatically finds 'RG4 7' sector.
        """
        school = School(
            name="TDD Academy",
            postcode="RG4 7SD"
        )
        school.save()
        
        # Expectation: The relationship is set automatically
        self.assertEqual(school.postcode_sector, self.sector)

    def test_school_validation_error_missing_sector(self):
        """
        Test that we cannot save a school if its sector doesn't exist.
        """
        school = School(
            name="Lost School",
            postcode="ZZ99 9ZZ" # Sector 'ZZ99 9' does not exist
        )
        # Expectation: save() raises ValidationError
        with self.assertRaises(ValidationError):
            school.save()

