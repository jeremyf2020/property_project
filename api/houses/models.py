from django.db import models
from api.coordinates.models import Coordinates
import re
from ..utils import auto_assign_sector, extract_sector_from_postcode
from django.core.exceptions import ValidationError

class HouseFeatures(models.Model):
    """
    Stores the combination of property characteristics.
    E.g., Detached, Freehold, New Build
    """
    # preserving original codes for compatibility
    TYPE_CHOICES = [
        ('D', 'Detached'),
        ('S', 'Semi-Detached'),
        ('T', 'Terraced'),
        ('F', 'Flats/Maisonettes'),
        ('O', 'Other'),
    ]
    TENURE_CHOICES = [('F', 'Freehold'), ('L', 'Leasehold')]

    # House characteristics
    type_code = models.CharField(max_length=1, choices=TYPE_CHOICES)
    tenure_code = models.CharField(max_length=1, choices=TENURE_CHOICES)
    is_new_build = models.BooleanField(default=False)

    class Meta:
        unique_together = ('type_code', 'tenure_code', 'is_new_build')

    def __str__(self):
        return f"{self.get_type_code_display()} - {self.get_tenure_code_display()}{' (' if self.is_new_build else ' (Not '}New Build)"

class Address(models.Model):
    """
    Stores the permanent physical location.
    """
    saon = models.CharField(max_length=255, blank=True, null=True, verbose_name="Secondary Address") # e.g. FLAT 2/ NUMBER 5 etc
    paon = models.CharField(max_length=255, verbose_name="Primary Address") # e.g. 17 - 19 / COX HOLLOW etc
    street = models.CharField(max_length=255) # e.g. VALPY STREET / SOUTHCOTE ROAD etc
    locality = models.CharField(max_length=255, blank=True, null=True) # e.g. WHITLEY WOOD /TILEHURST etc
    postcode = models.CharField(max_length=20) # e.g. RG1 1AR/RG30 2LA etc
    
    # LINK to postcode_sector Coordinate (use postcode is too large)
    postcode_sector = models.ForeignKey(
        Coordinates, 
        on_delete=models.CASCADE, 
        related_name='addresses'
    )

    class Meta:
        unique_together = ('paon', 'saon', 'postcode')

    def save(self, *args, **kwargs):
        """ auto-assign the sector """
        auto_assign_sector(self)
        super().save(*args, **kwargs)

    def __str__(self):
        addr = f"{self.paon} {self.street}" # e.g. "10 High St"
        if self.saon:
            addr = f"{self.saon}, {addr}" # e.g. "Flat 1, 10 High St"
        if self.locality:
            addr = f"{addr}, {self.locality}" # e.g. "10 High St, Caversham"
        return f"{addr}, {self.postcode}" # e.g. "10 High St, Caversham, RG4 8AA"
    
class HouseSale(models.Model):
    """
    a specific transaction history for an Address
    """
    unique_id = models.CharField(max_length=100, primary_key=True)
    price_paid = models.DecimalField(max_digits=12, decimal_places=2)
    deed_date = models.DateField()
    
    # Relationships
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='sales')
    # PROTECT to avoid deleting features in use (by other sale record)
    features = models.ForeignKey(HouseFeatures, on_delete=models.PROTECT) 

    def __str__(self):
        return f"£{self.price_paid} on {self.deed_date}"