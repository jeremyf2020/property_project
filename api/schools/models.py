from django.db import models
from api.coordinates.models import Coordinates
from api.utils import auto_assign_sector

class School(models.Model):
    """
    Official UK School Entity.
    """
    name = models.CharField(max_length=255)
    
    # Location
    street = models.CharField(max_length=255, blank=True, null=True)
    locality = models.CharField(max_length=255, blank=True, null=True)
    address3 = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=20)
    
    # Details
    school_type = models.CharField(max_length=100, blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    gender = models.CharField(max_length=20, blank=True, null=True)

    # Phase Flags
    is_primary = models.BooleanField(default=False)
    is_secondary = models.BooleanField(default=False)
    is_post16 = models.BooleanField(default=False)
    
    # Age Range (Integers allow for "Find schools for 4 year olds")
    minimum_age = models.IntegerField(null=True, blank=True)
    maximum_age = models.IntegerField(null=True, blank=True)

    # The Link
    postcode_sector = models.ForeignKey(Coordinates, on_delete=models.CASCADE, related_name='schools')

    def save(self, *args, **kwargs):
        """ auto-assign the sector """
        auto_assign_sector(self)
        super().save(*args, **kwargs)

    @property
    def phase(self):
        """
        Returns a single string describing the school phase.
        """
        if self.is_primary and self.is_secondary:
            return "All-through"
        if self.is_primary:
            return "Primary"
        if self.is_secondary:
            return "Secondary"
        if self.is_post16:
            return "Post-16"
        return "Not Specified"

    @property
    def age_range_str(self):
        """ Returns readable string '4-11' """
        if self.minimum_age is not None and self.maximum_age is not None:
            return f"{self.minimum_age}-{self.maximum_age}"
        return ""

    def __str__(self):
        return f"{self.name}"