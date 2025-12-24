from django.db import models
from api.coordinates.models import Coordinates

class CrimeCategory(models.Model):
    """
    Lookup table for crime types (e.g., 'Burglary', 'Drugs')
    """
    name = models.CharField(max_length=100, primary_key=True)

    def __str__(self):
        return self.name

class SectorCrimeStat(models.Model):
    """
    Links a Sector to a Category with a count.
    Row example: RG1 1 | Burglary | 12
    """
    sector = models.ForeignKey(
        Coordinates, 
        on_delete=models.CASCADE, 
        related_name='crime_stats'
    )
    category = models.ForeignKey(
        CrimeCategory, 
        on_delete=models.CASCADE
    )
    count = models.IntegerField(default=0)

    class Meta:
        unique_together = ('sector', 'category')

    def __str__(self):
        return f"{self.sector_id} - {self.category_id}: {self.count}"