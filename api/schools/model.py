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

    # The Link
    postcode_sector = models.ForeignKey(Coordinates, on_delete=models.CASCADE, related_name='schools')

    def save(self, *args, **kwargs):
        """ auto-assign the sector """
        auto_assign_sector(self)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}"