from django.db import models
from django.core.validators import RegexValidator
from django.db.models import Avg

class Coordinates(models.Model):
    """ Coordinates of UK Postcode Sectors """
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

    # --- crime rate ---
    population = models.IntegerField(default=0)
    households = models.IntegerField(default=0)
    total_crimes = models.IntegerField(default=0)

    @property
    def current_crime_rate(self):
        """Returns crimes per 1,000 households."""
        if self.households > 0:
            return round((self.total_crimes / self.households) * 1000, 2)
        return 0.0
    
    # --- transport ---
    def bus_stop_count(self):
        """
        Counts the number of bus stops linked to this sector.
        Returns 0 if no stops are found.
        """
        if hasattr(self, 'transport_stops'):
            return self.transport_stops.count()
        return 0

    def get_stops_with_routes(self):
        """
        Returns the QuerySet of stops, pre-loading routes for performance.
        Returns empty QuerySet if no stops exist.
        """
        if hasattr(self, 'transport_stops'):
            return self.transport_stops.prefetch_related('routes')
        return models.QuerySet(model=None) 

    # --- house price ---
    @property
    def area_average_price(self):
        """Calculates the average price of all house sales in this sector."""
        result = self.addresses.aggregate(avg=Avg('sales__price_paid'))
        return int(result['avg']) if result['avg'] else 0
    
    # --- School Names ---
    def get_school_names(self):
        """Returns a simple list of strings of nearby school names."""
        # Assumes related_name='schools' on School model
        return list(self.schools.values_list('name', flat=True))

    def __str__(self):
        return self.name