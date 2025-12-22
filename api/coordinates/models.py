from django.db import models
from django.core.validators import RegexValidator

class Coordinates(models.Model):
    name = models.CharField(
            max_length=20, 
            primary_key=True,
            validators=[
                RegexValidator(
                    regex=r'^[A-Z]{1,2}[0-9][A-Z0-9]? [0-9]$',
                    message="Name must be a valid UK Postcode Sector (e.g. 'RG1 1')."
                )
            ]
        )
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    nearby_sectors = models.ManyToManyField('self', blank=True, symmetrical=False)

    def __str__(self):
        return self.name