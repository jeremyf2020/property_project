from django.db import models

class Coordinates(models.Model):
    name = models.CharField(max_length=20, primary_key=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    nearby_sectors = models.ManyToManyField('self', blank=True, symmetrical=False)

    def __str__(self):
        return self.name