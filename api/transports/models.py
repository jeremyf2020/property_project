from django.db import models
from api.coordinates.models import Coordinates
from api.utils import auto_assign_sector

class BusRoute(models.Model):
    """
    Represents a Bus Number (e.g., "17", "21").
    """
    name = models.CharField(max_length=20, primary_key=True) 
    
    def __str__(self):
        return f"Bus {self.name}"

class TransportStop(models.Model):
    """
    A physical bus stop linked to a neighborhood (Sector) and multiple Bus Routes.
    """
    stop_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    
    # Links to the bus numbers that stop here
    routes = models.ManyToManyField(BusRoute, related_name='stops', blank=True)
    
    # Links to the nearest Postcode Sector (e.g. RG1 1)
    nearest_sector = models.ForeignKey(
        Coordinates, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='transport_stops'
    )

    def __str__(self):
        return f"{self.name} ({self.stop_id})"